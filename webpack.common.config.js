// Bundles static assets for loading in development environments.
// Optimizes for fast re-build time at the expense of a large bundle size.
const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  context: __dirname,
  entry: {
    // Application entry points
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

    // Entry point for bundling large amount of cldr-data json files separately from other vendor code
    globalization: './analytics_dashboard/static/js/utils/globalization',
  },

  resolve: {
    // For legacy reasons (when we used require.js), we need to add extra module resolving directories for some
    // `requires` in our javascript that use relative paths.
    modules: [
      'node_modules',
      'analytics_dashboard/static',
      'analytics_dashboard/static/js',
      'analytics_dashboard/static/apps',
    ],
    alias: {
      // Marionette in bower was called 'marionette'. In npm it's 'backbone.marionette'.
      marionette: 'backbone.marionette',
      // Internal Globalize.js code seems to expect 'cldr' to refer to this file in cldrjs.
      cldr: 'cldrjs/dist/cldr',

      // Aliases used in tests
      uitk: 'edx-ui-toolkit/src/js',
      URI: 'urijs/src/URI',

      // Dedupe copies of modules in bundles by forcing all dependencies to use our copy of the module they need:
      moment: path.resolve('./node_modules/moment'),
      jquery: path.resolve('./node_modules/jquery'),
      backbone: path.resolve('./node_modules/backbone'),
    },
  },

  output: {
    // Output bundles directly to the Django static assets directory
    path: path.resolve('./analytics_dashboard/static/bundles/'),
    // Tells clients to load bundles from the static route (uses CDN in production)
    publicPath: '/static/bundles/',
    // Bundle names will not change between builds if the content stays identical
    filename: '[name]-[chunkhash].js',
  },

  module: {
    // Specify file-by-file rules to Webpack. Some file-types need a particular kind of loader.
    rules: [
      // raw-loader just inlines files as a string in the javascript bundles
      {
        test: /\.underscore$/,
        use: 'raw-loader',
        include: path.join(__dirname, 'analytics_dashboard/static'),
        exclude: /node_modules/,
      },
      // Webpack, by default, uses the url-loader for images and fonts that are required/included by files it
      // processes, which just base64 encodes them and inlines them in the javascript bundles. This makes the
      // javascript bundles ginormous and defeats caching so we will use the file-loader instead to copy the files
      // directly to the output directory (the Django assets folder).
      {
        test: /\.(png|woff|woff2|eot|ttf|svg)$/,
        use: 'file-loader?name=fonts/[name].[ext]',
        include: [path.join(__dirname, 'analytics_dashboard/static'), path.join(__dirname, 'node_modules')],
      },
    ],
    // This option can increase build speed slightly by forcing Webpack to skip processing for some large
    // dependencies. Only add dependencies here that do not contain any `require`s or `include`s.
    noParse: [/cldr-data|underscore/],
  },

  // Specify additional processing or side-effects done on the Webpack output bundles as a whole.
  plugins: [
    // Logs all bundle information to a JSON file which is needed by Django as a reference for finding the actual
    // filenames on disk, which it doesn't know at runtime, from the bundle names, which it does know.
    new BundleTracker({
      filename: './webpack-stats.json',
    }),
    // We reference jquery as a global variable a lot. This plugin inlines a reference to the module in place of the
    // free variable.
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
    }),
    // This defines the theme that the SCSS should be building with
    new webpack.DefinePlugin({
      'process.env': {
        THEME_SCSS: JSON.stringify(process.env.THEME_SCSS || 'sass/themes/open-edx.scss'),
      },
    }),
    // AggressiveMergingPlugin in conjunction with these CommonChunkPlugins turns many GBs worth of individual
    // chunks into one or two large chunks that entry chunks reference. It reduces output bundle size a lot.
    new webpack.optimize.AggressiveMergingPlugin({ minSizeReduce: 1.1 }),
    new webpack.optimize.CommonsChunkPlugin({
      // Extracts code and json files for globalize.js into a separate bundle for efficient caching.
      names: 'globalization',
      minChunks: Infinity,
    }),
    new webpack.optimize.CommonsChunkPlugin({
      // Extracts every 3rd-party module common among all bundles into one chunk (excluding the modules in the
      // globalization bundle)
      name: 'manifest',
      minChunks(module, count) {
        return (
          module.context
                    && module.context.indexOf('node_modules') !== -1
                    && module.context.indexOf('cldr') === -1
                    && module.context.indexOf('globalize') === -1
        );
      },
    }),
    new webpack.optimize.CommonsChunkPlugin({
      // This chunk should only include the webpack runtime code. The runtime code changes on every webpack
      // compile. We extract this so that the hash on the above vendor chunk does not change on every webpack
      // compile (we don't want its hash to change without vendor lib changes, because that would bust the cache).
      name: 'manifest',
    }),
    // Enable this plugin to see a pretty tree map of modules in each bundle and how much size they take up.
    // new BundleAnalyzerPlugin({
    // analyzerMode: 'static'
    // })
  ],
};
