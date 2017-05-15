var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker'),
    ExtractTextPlugin = require('extract-text-webpack-plugin'),
    isProd = (process.env.NODE_ENV === ('production' || 'prod')),

    extractCSS = new ExtractTextPlugin('styles-css.css'),
    extractSCSS = new ExtractTextPlugin('styles-scss.css');

module.exports = {
    context: __dirname,
    entry: {
        'application-main': './analytics_dashboard/static/js/application-main',
        'engagement-content-main': './analytics_dashboard/static/js/engagement-content-main',
        'engagement-video-content-main': './analytics_dashboard/static/js/engagement-video-content-main',
        'engagement-videos-main': './analytics_dashboard/static/js/engagement-videos-main',
        'engagement-video-timeline-main': './analytics_dashboard/static/js/engagement-video-timeline-main',
        'enrollment-activity-main': './analytics_dashboard/static/js/enrollment-activity-main',
        'enrollment-geography-main': './analytics_dashboard/static/js/enrollment-geography-main',
        'enrollment-demographics-age-main': './analytics_dashboard/static/js/enrollment-demographics-age-main',
        'enrollment-demographics-education-main': './analytics_dashboard/static/js/enrollment-demographics-education-main',
        'enrollment-demographics-gender-main': './analytics_dashboard/static/js/enrollment-demographics-gender-main',
        'performance-content-main': './analytics_dashboard/static/js/performance-content-main',
        'performance-problems-main': './analytics_dashboard/static/js/performance-problems-main',
        'performance-answer-distribution-main': './analytics_dashboard/static/js/performance-answer-distribution-main',
        'learners-main': './analytics_dashboard/static/apps/learners/app/learners-main',
        'performance-learning-outcomes-content-main': './analytics_dashboard/static/js/performance-learning-outcomes-content-main',
        'performance-learning-outcomes-section-main': './analytics_dashboard/static/js/performance-learning-outcomes-section-main',
        'course-list-main': './analytics_dashboard/static/apps/course-list/app/course-list-main'
    },

    resolve: {
        modules: ['node_modules', 'analytics_dashboard/static', 'analytics_dashboard/static/js',
                  'analytics_dashboard/static/apps'],
        alias: {
            marionette: 'backbone.marionette',
            cldr: 'cldrjs/dist/cldr' // needed by globalize internally
        }
    },

    output: {
        path: path.resolve('./assets/bundles/'),
        publicPath: '/static/bundles/',
        filename: '[name]-[hash].js'
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        }),
        extractCSS,
        extractSCSS,
        // new webpack.optimize.CommonsChunkPlugin({names: 'common-chunks'})
        new webpack.optimize.AggressiveMergingPlugin(),
        new webpack.optimize.UglifyJsPlugin()
    ],

    module: {
        rules: [
            {test: /\.json$/, use: 'json-loader'},
            {test: /\.underscore$/, use: 'raw-loader'},
            {test: /\.(png|woff|woff2|eot|ttf|svg)$/, use: 'file-loader?name=assets/fonts/[name].[ext]'},
            {test: /\.scss$/, use: extractSCSS.extract({
                fallbackLoader: 'style-loader',
                loader: [{
                    loader: 'css-loader',
                    query: {
                        minimize: true
                    }
                }, {
                    loader: 'sass-loader',
                    query: {
                        minimize: true
                    }
                }]
            })},
            {test: /\.css$/, use: extractCSS.extract({
                fallbackLoader: 'style-loader',
                loader: {
                    loader: 'css-loader',
                    query: {
                        minimize: true
                    }
                }
            })}
        ]
    }
};
