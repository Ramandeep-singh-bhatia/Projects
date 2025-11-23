const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  return {
    entry: {
      // Background service worker
      'background/service-worker': './src/background/service-worker.ts',

      // Content scripts
      'content/content-script': './src/content/content-script.ts',

      // Popup
      popup: './src/popup/Popup.tsx',

      // Options page
      options: './src/options/Options.tsx',
    },

    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: '[name].js',
      clean: true,
    },

    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: 'ts-loader',
          exclude: /node_modules/,
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
      ],
    },

    resolve: {
      extensions: ['.tsx', '.ts', '.js'],
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },

    plugins: [
      // Copy static assets
      new CopyPlugin({
        patterns: [
          { from: 'public/manifest.json', to: 'manifest.json' },
          { from: 'public/icons', to: 'icons', noErrorOnMissing: true },
        ],
      }),

      // Generate HTML pages
      new HtmlWebpackPlugin({
        template: './public/popup.html',
        filename: 'popup.html',
        chunks: ['popup'],
      }),

      new HtmlWebpackPlugin({
        template: './public/options.html',
        filename: 'options.html',
        chunks: ['options'],
      }),
    ],

    devtool: isProduction ? false : 'inline-source-map',

    optimization: {
      minimize: isProduction,
    },
  };
};
