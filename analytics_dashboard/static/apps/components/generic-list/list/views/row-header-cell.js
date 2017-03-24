/**
 * Cell class which should be used to head a row of a backgrid table. This is an abstract class meant to be inherited,
 * not used directly.
 *
 * The contents of the cell may combine many values from the model. The entire model, as JSON, is sent to the template
 * during rendering.
 */
define(function(require) {
    'use strict';

    var Backgrid = require('backgrid'),

        RowHeaderCell;

    RowHeaderCell = Backgrid.Cell.extend({
        tagName: 'th',
        className: 'row-header-cell',  // override this in the subclass to give it a more specific class
        template: undefined,  // subclass and define your own template with _.template(require('text!...underscore'))
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            this.$el.attr('scope', 'row');
            return this;
        }
    });

    return RowHeaderCell;
});
