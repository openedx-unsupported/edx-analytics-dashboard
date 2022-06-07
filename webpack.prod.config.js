// Bundles static assets for loading in production environments.
// Optimizes for small resulting bundle size at the expense of a long build time.
const Merge = require('webpack-merge');
const path = require('path');
const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

const extractCSS = new ExtractTextPlugin('styles-css.css');
const extractSCSS = new ExtractTextPlugin('styles-scss.css');
const commonConfig = require('./webpack.common.config.js');

module.exports = Merge.smart(commonConfig, {
  module: {
    // Specify file-by-file rules to Webpack. Some file-types need a particular kind of loader.
    rules: [
      // The babel-loader transforms newer ES2015 syntax to older ES5 for legacy browsers.
      // The 'transform-runtime' plugin tells babel to require the runtime instead of inlining it (saves bundle
      // size).
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
            plugins: ['@babel/plugin-transform-runtime', '@babel/plugin-syntax-dynamic-import'],
          },
        },
      },
      // Webpack, by default, includes all CSS in the javascript bundles. Unfortunately, that means:
      // a) The CSS won't be cached by browsers separately (a javascript change will force CSS re-download)
      // b) Since CSS is applied asyncronously, it causes an ugly flash-of-unstyled-content.
      //
      // To avoid these problems, we extract the CSS from the bundles into separate CSS files that can be included
      // as <link> tags in the HTML <head> manually by our Django tempaltes.
      //
      // We will not do this in development because it prevents hot-reloading from working and it increases build
      // time.
      {
        test: /\.scss$/,
        use: extractSCSS.extract({
          fallback: 'style-loader',
          use: [
            {
              loader: 'css-loader', // creates the style nodes from JS strings
              options: {
                minimize: true,
                sourceMap: true,
              },
            },
            // converts relative font url paths in the pre-compiled pattern-library sass to webpack-friendly
            // paths by locating fonts from the source in node_modules.
            {
              loader: 'resolve-url-loader',
            },
            // fast-sass-loader might be slightly faster, but lacks useful source-map generation
            {
              loader: 'sass-loader', // compiles Sass to CSS.
              options: {
                minimize: true,
                sourceMap: true,
              },
            },
          ],
        }),
        exclude: /node_modules/,
      },
      // Not all of our dependencies use Sass. We need an additional rule for requiring or including CSS files.
      {
        test: /\.css$/,
        use: extractCSS.extract({
          fallback: 'style-loader',
          use: [
            {
              loader: 'css-loader',
              options: {
                minimize: true,
                sourceMap: true,
              },
            },
            {
              loader: 'resolve-url-loader',
            },
          ],
        }),
        include: [path.join(__dirname, 'analytics_dashboard/static'), path.join(__dirname, 'node_modules')],
      },
    ],
  },

  // Specify additional processing or side-effects done on the Webpack output bundles as a whole.
  plugins: [
    extractCSS,
    extractSCSS,
    new webpack.optimize.UglifyJsPlugin({ sourceMap: true }), // aka. minify
  ],

  // Source-map generation method. 'source-map' is the slowest, but also the highest quality.
  devtool: 'source-map',
});
