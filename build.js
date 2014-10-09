// TODO: Only include the listed modules in the dist directory
({
    mainConfigFile: "analytics_dashboard/static/js/config.js",
    baseUrl: "analytics_dashboard/static",
    dir: "analytics_dashboard/static/dist",
    removeCombined: true,
    findNestedDependencies: true,
    optimizeCss: false,
    skipDirOptimize: true,
    preserveLicenseComments: false,
    modules: [
        {
            name: "js/common"
        },
        {
            name: "js/config"
        },
        {
            name: "js/engagement-content-main",
            exclude: ["js/common"]
        },
        {
            name: "js/enrollment-activity-main",
            exclude: ["js/common"]
        },
        {
            name: "js/enrollment-geography-main",
            exclude: ["js/common"]
        }
    ]
})
