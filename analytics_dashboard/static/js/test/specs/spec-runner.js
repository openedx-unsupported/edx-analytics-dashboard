var context = require.context('../../../', true, /.+spec\.jsx?$/);
require('../../load/init-tooltips.js');
context.keys().forEach(context);
module.exports = context;
