var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  context: __dirname,

  entry: {
    InfoReader: './assets/js/info_reader/index.js',
    FeedReader: './assets/js/feed_reader/feed_reader.js',
    vendors: ['react'],
  },

  output: {
      path: path.resolve('./assets/bundles/'),
      filename: "[name]-[hash].js",
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
  ],

  module: {
    loaders: [
      {
        test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader',
        query:{
          presets:['react']
        }
      },
      { test: /\.css$/, loader: "style-loader!css-loader" },
    ]
  },

  resolve: {
    modules: ['node_modules', 'bower_components'],
    extensions: ['.js', '.jsx', '.css']
  },
}