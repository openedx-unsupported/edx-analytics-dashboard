const context = require.context('../../../', true, /.+spec\.jsx?$/);
require('../../load/init-tooltips');

context.keys().forEach(context);
module.exports = context;
