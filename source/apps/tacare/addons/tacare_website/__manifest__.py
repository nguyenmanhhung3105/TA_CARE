{
    "name": "TA.CARE Website",
    "summary": "Giao diện Kho Việc Làm, Tủ Hồ Sơ và TA.CARE",
    "version": "19.0.1.0.0",
    "category": "Website",
    "license": "LGPL-3",
    "depends": ["website"],
    "data": [
        "views/khovieclam.xml",
        "views/tuhoso.xml",
        "views/tacare.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "tacare_website/static/src/scss/website.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}