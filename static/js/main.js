$(document).ready(function() {

    $('.fileupload').fileupload()

    window.spacescout_admin = window.spacescout_admin || {};

    // general space functions
    window.spacescout_admin.getFieldValue = function (fv) {
        var i, v, fmt,
            t = [],
            value = function (vo) {
                var rv = '';

                switch (typeof vo.value) {
                case 'string':
                    rv = gettext(vo.value);
                    break;

                case 'number':
                    rv = String(vo.value);
                    break;

                case 'boolean':
                    rv = (vo.value) ? gettext(vo.key) : null;
                    break;
                    
                default:
                    break;
                };

                return rv;
            };

        if (fv && typeof fv === 'object') {
            if ($.isArray(fv)) {
                for (i = 0; i < fv.length; i += 1) {
                    if (fv[i].hasOwnProperty('value')) {
                        v = value(fv[i]);
                        if (v) {
                            t.push(v);
                        }
                    }
                }

                return t.join(', ');
            } else if (fv.hasOwnProperty('value')) {
                v = value(fv);
                if (v) {
                    return v;
                }
            }
        }

        return '';
    };

    window.spacescout_admin.prettyHours = function (hours) {
        var t = hours.match(/^(([01]?\d)|2[0123]):([012345]\d)$/),
            h, m;

        if (t) {
            h = parseInt(t[1]);
            m = parseInt(t[3]);

            if (m == 0) {
                if (h == 0 || h == 23) {
                    return gettext('midnight');
                } else if (h == 12) {
                    return gettext('noon');
                }
            }

            return ((h > 12) ? (h - 12) : h)
                + ':' + ((m < 10) ? ('0' + m) : m)
                + gettext((h > 11) ? 'pm' : 'am');
        }

        return hours;
    };

});