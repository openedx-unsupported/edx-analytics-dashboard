// Bundles static assets for loading in development environments.
// Optimizes for fast re-build time at the expense of a large bundle size.
const Merge = require('webpack-merge');
const path = require('path');
const commonConfig = require('./webpack.common.config.js');

const djangoDevServer = process.env.DJANGO_DEV_SERVER || 'http://localhost:8110';

webpackPort = process.env.WEBPACK_PORT || 8080;

module.exports = Merge.smart(commonConfig, {
  output: {
    // Tells clients to load bundles from the dev-server
    publicPath: `http://localhost:${webpackPort}/static/bundles/`,
    // Bundle names will change every build. [hash] is faster than [chunkhash].
    filename: '[name]-[hash].js',
  },

  module: {
    // Specify file-by-file rules to Webpack. Some file-types need a particular kind of loader.
    rules: [
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
            plugins: ['@babel/plugin-syntax-dynamic-import'],
            cacheDirectory: true,
          },
        },
      },
      // We are not extracting CSS from the javascript bundles in development because extracting prevents
      // hot-reloading from working, it increases build time, and we don't care about flash-of-unstyled-content
      // issues in development.
      {
        test: /\.scss$/,
        use: [
          {
            loader: 'style-loader', // creates style nodes from JS strings
          },
          {
            loader: 'css-loader', // translates CSS into CommonJS
            options: {
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
              sourceMap: true,
            },
          },
        ],
        exclude: /node_modules/,
      },
      // Not all of our dependencies use Sass. We need an additional rule for requiring or including CSS files.
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'resolve-url-loader'],
        include: [path.join(__dirname, 'analytics_dashboard/static'), path.join(__dirname, 'node_modules')],
      },
    ],
  },

  devServer: {
    compress: true,
    // Since the dev-server runs on a different port, browsers will complain about CORS violations unless we
    // explicitly tell them it's okay with this header.
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    host: '0.0.0.0',
    // Webpack does not process all images in Insights, so proxy all image requests through to django static files
    proxy: {
      // This assumes that the developer is running the django dev server on the default host and port
      '/static/images': djangoDevServer,
    },
  },

  // Source-map generation method. 'eval' is the fastest, but shouldn't be used in production (it increases file sizes
  // a lot). If source-maps are desired in production, 'source-map' should be used (slowest, but highest quality).
  devtool: 'eval',
  // devtool: 'cheap-module-source-map' // use this instead for better (but slightly slower) source-maps
});
