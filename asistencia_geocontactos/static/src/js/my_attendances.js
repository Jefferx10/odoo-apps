odoo.define('odoo_attendance_user_location.my_attendances', function(require) {
   /**
    * This class is used to get the checkin/out location of employee
    */
    "use strict";
    var MyAttendances = require("hr_attendance.my_attendances");
    var KioskConfirm = require("hr_attendance.kiosk_confirm");
    const session = require("web.session");
    var Dialog = require("web.Dialog");
    var core = require("web.core");
    var QWeb = core.qweb;
    var latitude;
    var longitude;
    MyAttendances.include({
        events: Object.assign({}, MyAttendances.prototype.events, {
            'change select[id="contactSelect"]': '_onChangeContactSelect',
        }),
        _onChangeContactSelect: function (ev) {
            if (this.$("#contactSelect")[0]) {
                const contactID = this.$("select[name='contact_id']").val();
                var selectHtml = '<select class="col-7" name="contact_task_id" id="contactTaskSelect">';
                selectHtml += '<option selected="selected" value=""></option>';
                selectHtml += "</select>";
                this.$("#contactTaskSelect").replaceWith(selectHtml);
            }
        },
        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._rpc({
                    model: 'hr.employee',
                    method: 'get_attendance_contact',
                    args: [[['user_id', '=', self.getSession().uid]]],
                    context: session.user_context,
                }).then(function (p) {
                    self.contacts = p;
                });
            });
        },
        update_attendance: function() {
        //To get current position of the employee
            var self = this;
            var partner_id = this.$("select[name='contact_id']").val();
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                        const ctx = Object.assign(session.user_context, {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            contact_id: partner_id,     
                        });
                        latitude = position.coords.latitude;
                        longitude = position.coords.longitude;
                        self._rpc({
                                model: 'hr.employee',
                                method: 'attendance_manual',
                                args: [
                                [self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'
                            ],
                                context: ctx,
                            })
                            .then(function(result) {
                                if (result.action) {
                                    self.do_action(result.action);
                                } else if (result.warning) {
                                    self.displayNotification({
                                        title: result.warning,
                                        type: 'danger'
                                    });
                                }
                            });
                    },
                    function(error) {
                        // Handle any errors
                        if (error) {
                            var MyDialog = new Dialog(null, {
                                title: error.__proto__.constructor.name,
                                size: "medium",
                                $content: this.$('<main/>', {
                                    role: 'alert',
                                    text: error['message'] + ". Also check your site connection is secured!",
                                }),
                                buttons: [{
                                    text: "OK",
                                    classes: "btn-primary",
                                    click: function() {
                                        MyDialog.close();
                                    }
                                }]
                            });
                            MyDialog.open();
                        }
                    });
            } else {
                this._rpc({
                        model: 'hr.employee',
                        method: 'attendance_manual',
                        args: [
                            [self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'
                        ],
                        context: context,
                    })
                    .then(function(result) {
                        if (result.action) {
                            self.do_action(result.action);
                        } else if (result.warning) {
                            self.displayNotification({
                                title: result.warning,
                                type: 'danger'
                            });
                        }
                    });
            }
        },
    });
   KioskConfirm.include({
        events: _.extend(KioskConfirm.prototype.events, {
            "click .o_hr_attendance_sign_in_out_icon": _.debounce(
                function() {
                //  Function to do on clicking sign out
                    var self = this;
                    var partner_id = this.$("select[name='contact_id']").val();
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(position) {
                                const ctx = Object.assign(session.user_context, {
                                    latitude: position.coords.latitude,
                                    longitude: position.coords.longitude,
                                });
                                latitude = position.coords.latitude;
                                longitude = position.coords.longitude;
                                self._rpc({
                                        model: 'hr.employee',
                                        method: 'attendance_manual',
                                        args: [
                                            [self.employee_id], self.next_action
                                        ],
                                        context: ctx,
                                    })
                                    .then(function(result) {
                                        if (result.action) {
                                            self.do_action(result.action);
                                        } else if (result.warning) {
                                            self.displayNotification({
                                                title: result.warning,
                                                type: 'danger'
                                            });
                                        }
                                    });
                            },
                            function(error) {
                                // Handle any errors
                                if (error) {
                                    var MyDialog = new Dialog(null, {
                                        title: error.__proto__.constructor.name,
                                        size: "medium",
                                        $content: self.$el.find('<main/>', {
                                            role: 'alert',
                                            text: error['message'] + ". Also check your site connection is secured!",
                                        }),
                                        buttons: [{
                                            text: "OK",
                                            classes: "btn-primary",
                                            click: function() {
                                                MyDialog.close();
                                            }
                                        }]
                                    });
                                    MyDialog.open();
                                }
                            });
                    }
                },
                200,
                true
            ),
            "click .o_hr_attendance_pin_pad_button_ok": _.debounce(
                function() {
            //    Pin pad button
                    var self = this;
                    this.pin_pad = true;
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(position) {
                                const ctx = Object.assign(session.user_context, {
                                    latitude: position.coords.latitude,
                                    longitude: position.coords.longitude,
                                });
                                latitude = position.coords.latitude;
                                longitude = position.coords.longitude;
                                self._rpc({
                                        model: 'hr.employee',
                                        method: 'attendance_manual',
                                        args: [
                                            [self.employee_id], self.next_action, self.$('.o_hr_attendance_PINbox')
                                            .val()
                                        ],
                                        context: session.user_context,
                                    })
                                    .then(function(result) {
                                        if (result.action) {
                                            self.do_action(result.action);
                                        } else if (result.warning) {
                                            self.displayNotification({
                                                title: result.warning,
                                                type: 'danger'
                                            });
                                            self.$('.o_hr_attendance_PINbox')
                                                .val('');
                                            setTimeout(function() {
                                                self.$('.o_hr_attendance_pin_pad_button_ok')
                                                    .removeAttr("disabled");
                                            }, 500);
                                        }
                                    });
                            },
                            function(error) {
                                // Handle any errors
                                if (error) {
                                    var MyDialog = new Dialog(null, {
                                        title: error.__proto__.constructor.name,
                                        size: "medium",
                                        $content: self.$.el.find('<main/>', {
                                            role: 'alert',
                                            text: error['message'] + ". Also check your site connection is secured!",
                                        }),
                                        buttons: [{
                                            text: "OK",
                                            classes: "btn-primary",
                                            click: function() {
                                                MyDialog.close();
                                            }
                                        }]
                                    });
                                    MyDialog.open();
                                }
                            });
                    }
                },
                200,
                true
            ),
        }),
    });
    return MyAttendances;
});
