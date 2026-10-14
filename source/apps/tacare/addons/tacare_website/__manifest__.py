{
    "name": "TA.CARE Website",
    "summary": "Giao diện Kho Việc Làm, Tủ Hồ Sơ và TA.CARE",
    "version": "19.0.2.0.0",
    "author": "TA.CARE",
    "category": "Website",
    "license": "LGPL-3",
    "depends": ["website", "tacare_account_access", "website_hr_recruitment", "hr_skills"],
    "data": [
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "views/khovieclam.xml",
        "views/tuhoso.xml",
        "views/tacare.xml",
        "views/hr_job_care.xml",
        "views/live.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "tacare_website/static/src/scss/website.scss",
            "tacare_website/static/src/scss/live.scss",
            "tacare_website/static/src/scss/live_polish.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
