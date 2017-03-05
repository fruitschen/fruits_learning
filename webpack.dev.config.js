var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

var config = require('./webpack.base.config.js')

// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = [
    new BundleTracker({filename: './webpack-stats.json'}),
],

// Add a loader for JSX files with react-hot enabled
config.module.loaders.push(
  {
    test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader',
    query:{
      presets:['react']
    }
  }
)

module.exports = config