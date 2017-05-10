var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker'),
    ExtractTextPlugin = require('extract-text-webpack-plugin'),
    BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin,
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
        'course-list-main': './analytics_dashboard/static/apps/course-list/app/course-list-main',
        globalization: './analytics_dashboard/static/js/utils/globalization'
    },

    resolve: {
        modules: ['node_modules', 'analytics_dashboard/static', 'analytics_dashboard/static/js',
                  'analytics_dashboard/static/apps'],
        alias: {
            marionette: 'backbone.marionette',
            cldr: 'cldrjs/dist/cldr', // needed by globalize internally
            // dedupe copies of modules in bundles by forcing all dependencies to use our copy of the module they need:
            moment: path.resolve('./node_modules/moment'),
            jquery: path.resolve('./node_modules/jquery'),
            backbone: path.resolve('./node_modules/backbone')
        }
    },

    output: {
        path: path.resolve('./assets/bundles/'),
        publicPath: 'http://localhost:8080/assets/bundles/',
        filename: '[name]-[hash].js'
    },

    plugins: [
        new BundleTracker({
            filename: './webpack-stats.json'
        }),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        }),
        extractCSS,
        extractSCSS,
        new webpack.optimize.AggressiveMergingPlugin({minSizeReduce: 1.1}),
        new webpack.optimize.CommonsChunkPlugin({
            // Extracts code and json files for globalize.js into a separate bundle for efficient caching.
            names: 'globalization',
            minChunks: Infinity
        }),
        new webpack.optimize.CommonsChunkPlugin({
            // Extracts every 3rd-party module common among all bundles into one "vendor" chunk (excluding the modules
            // in the globalization bundle)
            name: 'vendor',
            minChunks(module, count) {
                return module.context && module.context.indexOf('node_modules') !== -1 &&
                       module.context.indexOf('cldr') === -1 &&
                       module.context.indexOf('globalize') === -1;
            },
        }),
        new webpack.optimize.CommonsChunkPlugin({
            // This chunk should only include the webpack runtime code. The runtime code changes on every webpack
            // compile. We extract this so that the hash on the above vendor chunk does not change on every webpack
            // compile (we don't want its hash to change without vendor lib changes, because that would bust the cache).
            name: 'manifest',
        }),
        // enable this to see a pretty tree map of modules in each bundle and how much size they take up
        // new BundleAnalyzerPlugin({
            // analyzerMode: 'static'
        // }),
        new webpack.optimize.UglifyJsPlugin()
    ],

    module: {
        rules: [
            // {test: /\.json$/, use: 'json-loader'},
            {
                test: /\.underscore$/,
                use: 'raw-loader',
                include: path.join(__dirname, 'analytics_dashboard/static'),
                exclude: /node_modules/
            },
            {
                test: /\.(png|woff|woff2|eot|ttf|svg)$/,
                use: 'file-loader?name=fonts/[name].[ext]',
                include: [
                    path.join(__dirname, 'analytics_dashboard/static'),
                    path.join(__dirname, 'node_modules')
                ]
            },
            {
                test: /\.scss$/,
                use: extractSCSS.extract({
                    fallback: 'style-loader',
                    use: [{
                        loader: 'css-loader',
                        query: {
                            minimize: true
                        }
                    }, {
                        loader: 'fast-sass-loader',
                        query: {
                            minimize: true
                        }
                    }]
                }),
                exclude: /node_modules/
            },
            {
                test: /\.css$/,
                use: extractCSS.extract({
                    fallback: 'style-loader',
                    use: {
                        loader: 'css-loader',
                        query: {
                            minimize: true
                        }
                    }
                }),
                include: [
                    path.join(__dirname, 'analytics_dashboard/static'),
                    path.join(__dirname, 'node_modules')
                ]
            }
        ],
        noParse: [/cldr-data|underscore/]
    },

    devServer: {
        compress: true,
        headers: {
            'Access-Control-Allow-Origin': '*',
        }, 
        // webpack does not process all images, proxy them through to django static files
        proxy: {
            // This assumes that the developer is running the django dev server on the default host and port
            '/static/images': 'http://localhost:9000'
        }
    },

    // Source-map generation method. 'eval' is the fastest, but shouldn't be used in production (it increases file sizes
    // a lot). If source-maps are desired in production, 'source-map' should be used (slowest, but highest quality).
    devtool: 'eval'
};
