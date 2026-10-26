#!/usr/bin/env python3
"""Prepare and restore-check a PRIVATE full local release; never SSH or push.

Preview by default. --prepare pauses local Odoo for a consistent database and
filestore backup, then verifies a disposable local restore and addon upgrade.
The original (not neutralized) dump is packaged with exact-commit addon code.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import uuid

ROOT = Path(__file__).resolve().parents[2]
ADDONS = 'source/apps/tacare/addons'
SOURCE_DB = 'tacare_local'
COUNTS_SQL = """SELECT json_build_object(
 'users',(SELECT count(*) FROM res_users),
 'partners',(SELECT count(*) FROM res_partner),
 'jobs',(SELECT count(*) FROM hr_job),
 'profiles',(SELECT count(*) FROM tacare_profile),
 'offers',(SELECT count(*) FROM care_profile_capability),
 'attachments',(SELECT count(*) FROM ir_attachment),
 'ownerless_jobs',(SELECT count(*) FROM hr_job j LEFT JOIN res_users u ON u.id=j.tacare_owner_user_id
     WHERE j.care_opportunity_kind='flexible' AND (u.id IS NULL OR NOT u.active OR j.tacare_owner_partner_id IS NULL)),
 'ownerless_profiles',(SELECT count(*) FROM tacare_profile p LEFT JOIN res_users u ON u.id=p.user_id WHERE u.id IS NULL OR NOT u.active),
 'ownerless_offers',(SELECT count(*) FROM care_profile_capability c LEFT JOIN tacare_profile p ON p.id=c.profile_id WHERE p.id IS NULL),
 'recruitment_jobs',(SELECT count(*) FROM hr_job WHERE care_opportunity_kind='recruitment'),
 'recruitment_profiles',(SELECT count(*) FROM tacare_profile WHERE care_recruitment_enabled),
 'jobs_outside_kho',(SELECT count(*) FROM hr_job WHERE company_id IS DISTINCT FROM
     (SELECT company_id FROM website WHERE care_site_kind='khovieclam')),
 'profiles_outside_tu',(SELECT count(*) FROM tacare_profile WHERE company_id IS DISTINCT FROM
     (SELECT company_id FROM website WHERE care_site_kind='tuhoso')));"""
ZERO_COUNTS = ('ownerless_jobs','ownerless_profiles','ownerless_offers','recruitment_jobs',
               'recruitment_profiles','jobs_outside_kho','profiles_outside_tu')


def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def docker(*args, **kwargs):
    return run(['docker','compose',*args], **kwargs)


def sql(database, statement):
    return json.loads(docker('exec','-T','db','psql','-X','-v','ON_ERROR_STOP=1',
        '-U','postgres','-d',database,'-Atc',statement,capture_output=True,text=True).stdout)


def metadata(path):
    with path.open('rb') as f:
        return dict(bytes=path.stat().st_size, sha256=hashlib.file_digest(f,'sha256').hexdigest())


def checked_members(archive):
    members=archive.getmembers()
    if len({m.name for m in members})!=len(members):
        raise ValueError('Duplicate filestore archive paths')
    for m in members:
        path=PurePosixPath(m.name)
        if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!=SOURCE_DB or not (m.isfile() or m.isdir()):
            raise ValueError('Unsafe filestore archive member')
    return members


def private_json(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    path.chmod(0o600)


def prepare():
    os.umask(0o077)
    sha=run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
    dirty=run(['git','status','--porcelain','--',ADDONS],capture_output=True,text=True).stdout
    if dirty:
        raise RuntimeError('Commit reviewed addon changes before making an exact-commit package')
    before=sql(SOURCE_DB,COUNTS_SQL)
    if any(before[k] for k in ZERO_COUNTS):
        raise RuntimeError('Owner/product/seasonal-only integrity checks failed')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=ROOT/'backups'/('full_local_release_'+stamp)
    release=ROOT/'runtime/releases'/('full-local-restore-'+sha[:7]+'-'+stamp)
    backup.mkdir(mode=0o700); release.mkdir(parents=True,mode=0o700)
    try:
        docker('stop','tacare',stdout=subprocess.DEVNULL)
        # The stopped application cannot change attachments while the pair is exported.
        before=sql(SOURCE_DB,COUNTS_SQL)
        with (backup/'tacare_local.dump').open('xb') as stream:
            docker('exec','-T','db','pg_dump','-U','postgres','-Fc','--no-owner','--no-acl',SOURCE_DB,stdout=stream)
        with (backup/'filestore.tar.gz').open('xb') as stream:
            docker('run','--rm','--no-deps','--entrypoint','tar','tacare','-czf','-','-C','/var/lib/odoo/filestore',SOURCE_DB,stdout=stream)
    finally:
        docker('up','-d','tacare',stdout=subprocess.DEVNULL)
    temporary='tacare_releasecheck_'+uuid.uuid4().hex[:12]
    stage_store=ROOT/'runtime/tacare/filestore'/temporary
    created=False
    try:
        docker('exec','-T','db','createdb','-U','postgres','-O','odoo',temporary)
        created=True
        with (backup/'tacare_local.dump').open('rb') as stream, (release/'restore-check.log').open('xb') as log:
            docker('exec','-T','db','pg_restore','-U','postgres','--role=odoo','--no-owner','--no-acl',
                   '--exit-on-error','-d',temporary,stdin=stream,stdout=log,stderr=subprocess.STDOUT)
        restored=sql(temporary,COUNTS_SQL)
        if restored!=before:
            raise RuntimeError('Restored database counts/ownership do not match the source snapshot')
        references=sql(temporary,"SELECT coalesce(json_agg(json_build_object('path',store_fname,'bytes',file_size,'sha1',checksum)), '[]'::json) FROM ir_attachment WHERE store_fname IS NOT NULL")
        with tarfile.open(backup/'filestore.tar.gz','r:gz') as archive:
            members=checked_members(archive)
            for item in references:
                relative=PurePosixPath(item['path'])
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('Unsafe attachment reference')
                member=archive.getmember(SOURCE_DB+'/'+item['path'])
                with archive.extractfile(member) as stream:
                    checksum=hashlib.file_digest(stream,'sha1').hexdigest()
                if member.size!=item['bytes'] or checksum!=item['sha1']:
                    raise RuntimeError('Referenced attachment integrity failed')
            stage_store.mkdir(mode=0o700)
            for member in members:
                relative=PurePosixPath(member.name).relative_to(SOURCE_DB)
                target=stage_store.joinpath(*relative.parts)
                if member.isdir():
                    target.mkdir(parents=True,exist_ok=True,mode=0o700)
                else:
                    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                    with archive.extractfile(member) as source, target.open('xb') as output:
                        shutil.copyfileobj(source,output)
                    target.chmod(0o600)
            file_count=sum(m.isfile() for m in members)
        # Only this disposable clone is neutralized. Never package this stage DB.
        with (release/'stage-neutralize.log').open('xb') as log:
            docker('run','--rm','--no-deps','-T','tacare','neutralize','-c','/etc/odoo/local.conf',
                   '-d',temporary,stdout=log,stderr=subprocess.STDOUT)
        with (release/'stage-upgrade.log').open('xb') as log:
            docker('run','--rm','--no-deps','-T','tacare','-c','/etc/odoo/local.conf','-d',temporary,
                   '-u','tacare_account_access,tacare_website','--stop-after-init','--no-http',
                   '--max-cron-threads=0',stdout=log,stderr=subprocess.STDOUT)
        after_stage=sql(temporary,COUNTS_SQL)
        if any(after_stage[k] for k in ZERO_COUNTS) or any(after_stage[k]!=before[k] for k in ('users','partners','jobs','profiles','offers')):
            raise RuntimeError('Disposable addon upgrade changed marketplace identity/counts')
    finally:
        if created:
            assert re.fullmatch(r'tacare_releasecheck_[0-9a-f]{12}',temporary)
            docker('exec','-T','db','dropdb','-U','postgres',temporary)
        if stage_store.exists():
            assert stage_store.parent==ROOT/'runtime/tacare/filestore' and stage_store.name==temporary
            shutil.rmtree(stage_store)
    addons=release/'addons.tar.gz'
    with addons.open('xb') as output:
        run(['git','archive','--format=tar.gz',sha,ADDONS],stdout=output)
    verification=dict(local_restore='passed',local_neutralized_addon_upgrade='passed',
        source_counts=before,restored_counts=restored,referenced_attachment_files_verified=len(references),
        missing_attachment_files=0,filestore_files=file_count,server_staging='not performed')
    manifest=dict(format='tacare.full-local-restore.v1',requires_manual_restore=True,
        accepted_strategy='replace_database_and_filestore',source_database=SOURCE_DB,source_commit=sha,
        created_at=datetime.now(timezone.utc).isoformat(),verification=verification,
        files={name:metadata(path) for name,path in [('tacare_local.dump',backup/'tacare_local.dump'),
             ('filestore.tar.gz',backup/'filestore.tar.gz'),('addons.tar.gz',addons)]},
        production_configuration='Must inspect live scripts/configuration and adapt domains, sessions, mail and cron; localhost operational files are excluded',
        core_reference_files={})
    for name in ('odoo/release.py','requirements.txt'):
        path=ROOT/'source/odoo-server'/name
        if path.is_file():manifest['core_reference_files'][name]=metadata(path)['sha256']
    private_json(backup/'manifest.json',manifest)
    private_json(release/'manifest.json',manifest)
    package=release/'full-local-restore.tar.gz'
    with tarfile.open(package,'x:gz') as archive:
        for name,path in [('tacare_local.dump',backup/'tacare_local.dump'),('filestore.tar.gz',backup/'filestore.tar.gz'),
                          ('addons.tar.gz',addons),('manifest.json',release/'manifest.json')]:
            archive.add(path,arcname='full-local-restore/'+name,recursive=False)
    with tarfile.open(package,'r:gz') as archive:
        if set(archive.getnames())!={'full-local-restore/'+name for name in ['tacare_local.dump','filestore.tar.gz','addons.tar.gz','manifest.json']}:
            raise RuntimeError('Unexpected release package contents')
        for name,expected in manifest['files'].items():
            with archive.extractfile('full-local-restore/'+name) as stream:
                if hashlib.file_digest(stream,'sha256').hexdigest()!=expected['sha256']:
                    raise RuntimeError('Packaged file checksum mismatch')
    report=dict(status='local_verified_awaiting_server_inspection',package=str(package.relative_to(ROOT)),
        backup=str(backup.relative_to(ROOT)),source_commit=sha,**metadata(package),verification=verification,
        uploaded=False,deployed=False)
    private_json(ROOT/'runtime/releases/current-full-local-restore.json',report)
    print('PASS full snapshot: restore, referenced attachments, neutralized local addon upgrade, ownership, exact-commit code and checksums')
    print('PACKAGE',report['package'])
    print('COUNTS',json.dumps(before))
    print('No server upload/restore, Git push or production change was performed')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true',help='Create and verify a full private local release')
    args=parser.parse_args()
    if args.prepare:
        prepare()
    else:
        print('Preview: exact HEAD addons + tacare_local dump + filestore, private outputs only. Use --prepare after reviewing/committing addons. No SSH or push.')
