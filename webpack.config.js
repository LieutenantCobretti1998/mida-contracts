import path from 'path';
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export default {
  mode: 'development',
  entry: {
    tableForContracts: path.resolve(__dirname, './static/js/contracts_table.js'),
    tableForCompanies: path.resolve(__dirname, './static/js/companies_table.js'),
    tableForActs: path.resolve(__dirname, './static/js/acts_table.js'),
    tableForCategories: path.resolve(__dirname, './static/js/categories_table.js'),
    tableForAdditions: path.resolve(__dirname, './static/js/addition_table.js'),
  },
  output: {
    filename: "[name].bundle.js",
    path: path.resolve(__dirname, './static/js/'),
     library: {
      type: 'module', // Export as an ES module
    },
  },
  experiments: {
    outputModule: true
  },
  resolve: {
    alias: {
      gridJs: path.resolve(__dirname, './node_modules/gridjs'),
    },
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      }
    ]
  },
  watch: true,
};
