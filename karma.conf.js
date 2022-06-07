// Karma configuration
// Generated on Thu Jun 26 2014 17:49:39 GMT-0400 (EDT)

const path = require('path');
const webpack = require('webpack');

module.exports = function (config) {
  'use strict';

  config.set({
    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',

    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine-jquery', 'jasmine', 'sinon'],

    // list of files / patterns to load in the browser
    files: [
      { pattern: 'node_modules/**/*.js', included: false },
      { pattern: 'node_modules/**/*.underscore', included: false },
      // limiting the cldr json files to load (we don't use the other ones and loading too many
      // throws errors on a mac)
      { pattern: 'node_modules/cldr-data/supplemental/*.json', included: false },
      { pattern: 'node_modules/cldr-data/availableLocales.json', included: false },
      { pattern: 'node_modules/cldr-data/**/numbers.json', included: false },
      { pattern: 'analytics_dashboard/static/js/load/*.js', included: false },
      { pattern: 'analytics_dashboard/static/js/models/**/*.js', included: false },
      { pattern: 'analytics_dashboard/static/js/views/**/*.js', included: false },
      { pattern: 'analytics_dashboard/static/js/utils/**/*.js', included: false },
      { pattern: 'analytics_dashboard/static/apps/**/*.underscore', included: false },

      // actual tests
      { pattern: 'analytics_dashboard/static/js/test/specs/spec-runner.js' },
    ],

    exclude: [
      // Don't run library unit tests
      'node_modules/**/spec/**/*.js',
      'node_modules/**/specs/**/*.js',
      'node_modules/**/test/**/*.js',
    ],

    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'analytics_dashboard/static/js/test/specs/spec-runner.js': ['webpack', 'sourcemap'],
    },

    // plugins required for running the karma tests
    plugins: [
      'karma-jasmine',
      'karma-jasmine-jquery-2',
      'karma-jasmine-html-reporter',
      'karma-phantomjs-launcher',
      'karma-coverage',
      'karma-sinon',
      'karma-chrome-launcher',
      'karma-webpack',
      'karma-sourcemap-loader',
      'karma-coverage-istanbul-reporter'
    ],

    webpack: {
      // For detailed comments about webpack configuration, see webpack.config.js or webpack.prod.config.js
      // This is just slimmed down version of webpack.config.js just for running karma tests
      context: __dirname,
      resolve: {
        modules: [
          'node_modules',
          'analytics_dashboard/static',
          'analytics_dashboard/static/js',
          'analytics_dashboard/static/apps',
        ],
        alias: {
          marionette: 'backbone.marionette',
          cldr: 'cldrjs/dist/cldr',

          // Aliases used in tests
          uitk: 'edx-ui-toolkit/src/js',
          URI: 'urijs/src/URI',

          moment: path.resolve('./node_modules/moment'),
          jquery: path.resolve('./node_modules/jquery'),
          backbone: path.resolve('./node_modules/backbone'),
        },
      },

      output: {
        path: path.resolve('./assets/bundles/'),
        filename: '[name]-[hash].js',
      },

      module: {
        rules: [
          {
            test: /\.underscore$/,
            use: 'raw-loader',
            include: path.join(__dirname, 'analytics_dashboard/static'),
            exclude: /node_modules/,
          },
          {
            test: /\.(png|woff|woff2|eot|ttf|svg)$/,
            use: 'file-loader?name=fonts/[name].[ext]',
            include: [
              path.join(__dirname, 'analytics_dashboard/static'),
              path.join(__dirname, 'node_modules'),
            ],
          },
          // The babel-loader transforms newer ES2015 syntax to older ES5 for legacy browsers.
          {
            test: /\.js$/,
            exclude: /(node_modules|bower_components)/,
            use: {
              loader: 'babel-loader',
              options: {
                presets: [
                  ['@babel/preset-env', {
                    targets: {
                      browsers: ['last 2 versions', 'ie >= 11'],
                    },
                  }],
                ],
                plugins: [
                  '@babel/plugin-syntax-dynamic-import',
                  ['istanbul', {
                    exclude: [
                      '**/*spec.js',
                    ],
                  }],
                ],
                cacheDirectory: true,
              },
            },
          },
          {
            test: /\.scss$/,
            use: [
              {
                loader: 'style-loader', // creates style nodes from JS strings
              },
              {
                loader: 'css-loader', // translates CSS into CommonJS
              },
              {
                loader: 'fast-sass-loader', // compiles Sass to CSS. If this breaks, just use sass-loader
              },
            ],
            exclude: /node_modules/,
          },
          {
            test: /\.css$/,
            use: ['style-loader', 'css-loader'],
            include: [
              path.join(__dirname, 'analytics_dashboard/static'),
              path.join(__dirname, 'node_modules'),
            ],
          },
        ],
        noParse: [/cldr-data|underscore/],
      },

      plugins: [
        new webpack.ProvidePlugin({
          $: 'jquery',
          jQuery: 'jquery',
          // the Insights application loads gettext identity library via django, thus
          // components reference gettext globally so a shim is added here to reflect
          // the text so tests can be run if modules reference gettext
          gettext: 'test/browser-shims/gettext',
          ngettext: 'test/browser-shims/ngettext',
        }),
        // This defines the theme that the SCSS should be building with. For test, this is always open-edx
        new webpack.DefinePlugin({
          'process.env': {
            THEME_SCSS: 'sass/themes/open-edx.scss',
          },
        }),
      ],

      devtool: 'inline-source-map',
    },

    webpackMiddleware: {
      // silences most webpack log output
      noInfo: true,
    },

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage-istanbul'],

    coverageIstanbulReporter: {
      dir: 'build',
      subdir: 'coverage-js',
      reporters: [
        { type: 'html', subdir: 'coverage-js/html' },
        { type: 'cobertura', file: 'coverage.xml' },
        { type: 'text-summary' },
      ],
      fixWebpackSourcePaths: true
    },

    // web server port
    port: 9876,

    // enable / disable colors in the output (reporters and logs)
    colors: true,

    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN
    // || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,

    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    // you can also add Chrome or other browsers too
    browsers: ['PhantomJS'],

    captureTimeout: 60000,

    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false,
  });
};
