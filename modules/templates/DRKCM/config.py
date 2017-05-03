# -*- coding: utf-8 -*-

import datetime

from collections import OrderedDict

from gluon import current, SPAN
from gluon.storage import Storage

from s3 import FS, IS_ONE_OF, S3DateTime, S3Method, s3_str, s3_unicode

def config(settings):
    """
        DRKCM Template: Case Management, German Red Cross
    """

    T = current.T

    settings.base.system_name = "Case Management"
    settings.base.system_name_short = "Case Management"

    # PrePopulate data
    settings.base.prepopulate += ("DRKCM", "default/users", "DRKCM/Demo")

    # Theme (folder to use for views/layout.html)
    settings.base.theme = "DRK"

    # Authentication settings
    # Should users be allowed to register themselves?
    settings.security.self_registration = False
    # Do new users need to verify their email address?
    #settings.auth.registration_requires_verification = True
    # Do new users need to be approved by an administrator prior to being able to login?
    #settings.auth.registration_requires_approval = True
    settings.auth.registration_requests_organisation = True
    settings.auth.registration_link_user_to = {"staff": T("Staff"),
                                               "volunteer": T("Volunteer"),
                                               }
    #settings.auth.registration_link_user_to_default = "staff"

    # Approval emails get sent to all admins
    settings.mail.approver = "ADMIN"

    # Restrict the Location Selector to just certain countries
    # NB This can also be over-ridden for specific contexts later
    # e.g. Activities filtered to those of parent Project
    settings.gis.countries = ("DE",)
    # Uncomment to display the Map Legend as a floating DIV
    settings.gis.legend = "float"
    # Uncomment to Disable the Postcode selector in the LocationSelector
    #settings.gis.postcode_selector = False # @ToDo: Vary by country (include in the gis_config!)
    # Uncomment to show the Print control:
    # http://eden.sahanafoundation.org/wiki/UserGuidelines/Admin/MapPrinting
    #settings.gis.print_button = True

    # Settings suitable for Housing Units
    # - move into customise fn if also supporting other polygons
    settings.gis.precision = 5
    settings.gis.simplify_tolerance = 0
    settings.gis.bbox_min_size = 0.001
    #settings.gis.bbox_offset = 0.007

    # L10n settings
    # Languages used in the deployment (used for Language Toolbar & GIS Locations)
    # http://www.loc.gov/standards/iso639-2/php/code_list.php
    settings.L10n.languages = OrderedDict([
       ("de", "Deutsch"),
       ("en", "English"),
    ])
    # Default language for Language Toolbar (& GIS Locations in future)
    settings.L10n.default_language = "de"
    # Uncomment to Hide the language toolbar
    #settings.L10n.display_toolbar = False
    # Default timezone for users
    #settings.L10n.utc_offset = "+0100"
    # Number formats (defaults to ISO 31-0)
    # Decimal separator for numbers (defaults to ,)
    settings.L10n.decimal_separator = "."
    # Thousands separator for numbers (defaults to space)
    settings.L10n.thousands_separator = ","
    # Uncomment this to Translate Layer Names
    #settings.L10n.translate_gis_layer = True
    # Uncomment this to Translate Location Names
    #settings.L10n.translate_gis_location = True
    # Uncomment this to Translate Organisation Names/Acronyms
    #settings.L10n.translate_org_organisation = True
    # Finance settings
    settings.fin.currencies = {
        "EUR" : "Euros",
    #    "GBP" : "Great British Pounds",
    #    "USD" : "United States Dollars",
    }
    settings.fin.currency_default = "EUR"

    # Security Policy
    # http://eden.sahanafoundation.org/wiki/S3AAA#System-widePolicy
    # 1: Simple (default): Global as Reader, Authenticated as Editor
    # 2: Editor role required for Update/Delete, unless record owned by session
    # 3: Apply Controller ACLs
    # 4: Apply both Controller & Function ACLs
    # 5: Apply Controller, Function & Table ACLs
    # 6: Apply Controller, Function, Table ACLs and Entity Realm
    # 7: Apply Controller, Function, Table ACLs and Entity Realm + Hierarchy
    # 8: Apply Controller, Function, Table ACLs, Entity Realm + Hierarchy and Delegations
    #
    settings.security.policy = 5 # Controller, Function & Table ACLs

    # Version details on About-page require login
    settings.security.version_info_requires_login = True

    # -------------------------------------------------------------------------
    # CMS Module Settings
    #
    settings.cms.hide_index = True

    # -------------------------------------------------------------------------
    # Human Resource Module Settings
    #
    settings.hrm.teams_orgs = False

    # -------------------------------------------------------------------------
    # Inventory Module Settings
    #
    settings.inv.facility_label = "Facility"
    settings.inv.facility_manage_staff = False

    # -------------------------------------------------------------------------
    # Organisations Module Settings
    #
    settings.org.default_organisation = "Deutsches Rotes Kreuz"
    settings.org.default_site = "BEA Benjamin Franklin Village"

    # -------------------------------------------------------------------------
    # Persons Module Settings
    #
    settings.pr.hide_third_gender = False
    settings.pr.separate_name_fields = 2
    settings.pr.name_format= "%(last_name)s, %(first_name)s"

    # -------------------------------------------------------------------------
    # Project Module Settings
    #
    settings.project.mode_task = True
    settings.project.sectors = False

    # NB should not add or remove options, but just comment/uncomment
    settings.project.task_status_opts = {#1: T("Draft"),
                                         2: T("New"),
                                         3: T("Assigned"),
                                         #4: T("Feedback"),
                                         #5: T("Blocked"),
                                         6: T("On Hold"),
                                         7: T("Canceled"),
                                         #8: T("Duplicate"),
                                         #9: T("Ready"),
                                         #10: T("Verified"),
                                         #11: T("Reopened"),
                                         12: T("Completed"),
                                         }

    settings.project.task_time = False
    settings.project.my_tasks_include_team_tasks = True

    # -------------------------------------------------------------------------
    # Requests Module Settings
    #
    settings.req.req_type = ("Stock",)
    settings.req.use_commit = False
    settings.req.recurring = False

    # -------------------------------------------------------------------------
    # Shelter Module Settings
    #
    #settings.cr.day_and_night = False
    settings.cr.shelter_population_dynamic = True
    settings.cr.shelter_housing_unit_management = True
    settings.cr.check_out_is_final = False

    # Generate tasks for shelter inspections
    settings.cr.shelter_inspection_tasks = True
    settings.cr.shelter_inspection_task_active_statuses = (2, 3, 6)

    # -------------------------------------------------------------------------
    def customise_auth_user_resource(r, tablename):

        current.db.auth_user.organisation_id.default = settings.get_org_default_organisation()

    settings.customise_auth_user_resource = customise_auth_user_resource

    # -------------------------------------------------------------------------
    def customise_cr_shelter_controller(**attr):

        s3 = current.response.s3

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):
            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            has_role = current.auth.s3_has_role
            if has_role("SECURITY") and not has_role("ADMIN"):
                # Security can access nothing in cr/shelter except
                # Dashboard and Check-in/out UI
                current.auth.permission.fail()

            if r.interactive:

                resource = r.resource
                resource.configure(filter_widgets = None,
                                   insertable = False,
                                   deletable = False,
                                   )

            if r.component_name == "shelter_unit":
                # Expose "transitory" flag for housing units
                utable = current.s3db.cr_shelter_unit
                field = utable.transitory
                field.readable = field.writable = True
                list_fields = ["name",
                               "transitory",
                               "capacity_day",
                               "population_day",
                               "available_capacity_day",
                               ]
                r.component.configure(list_fields=list_fields)

            return result
        s3.prep = custom_prep

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            # Custom view for shelter inspection
            if r.method == "inspection":
               from s3 import S3CustomController
               S3CustomController._view("DRK", "shelter_inspection.html")

            return output
        s3.postp = custom_postp

        attr = dict(attr)
        attr["rheader"] = drk_cr_rheader

        return attr

    settings.customise_cr_shelter_controller = customise_cr_shelter_controller

    # -------------------------------------------------------------------------
    def customise_cr_shelter_registration_resource(r, tablename):

        table = current.s3db.cr_shelter_registration
        field = table.shelter_unit_id

        # Filter to available housing units
        from gluon import IS_EMPTY_OR
        field.requires = IS_EMPTY_OR(IS_ONE_OF(current.db, "cr_shelter_unit.id",
                                               field.represent,
                                               filterby = "status",
                                               filter_opts = (1,),
                                               orderby="shelter_id",
                                               ))

    settings.customise_cr_shelter_registration_resource = customise_cr_shelter_registration_resource

    # -------------------------------------------------------------------------
    def customise_cr_shelter_registration_controller(**attr):
        """
            Shelter Registration controller is just used
            by the Quartiermanager role.
        """

        s3 = current.response.s3

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):
            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            if r.method == "assign":

                # Prep runs before split into create/update (Create should never happen in Village)
                table = r.table
                shelter_id = drk_default_shelter()
                if shelter_id:
                    # Only 1 Shelter
                    f = table.shelter_id
                    f.default = shelter_id
                    f.writable = False # f.readable kept as True for cr_shelter_registration_onvalidation
                    f.comment = None

                # Only edit for this Person
                f = table.person_id
                f.default = r.get_vars["person_id"]
                f.writable = False
                f.comment = None
                # Registration status hidden
                f = table.registration_status
                f.readable = False
                f.writable = False
                # Check-in dates hidden
                f = table.check_in_date
                f.readable = False
                f.writable = False
                f = table.check_out_date
                f.readable = False
                f.writable = False

                # Go back to the list of residents after assigning
                from gluon import URL
                current.s3db.configure("cr_shelter_registration",
                                       create_next = URL(c="dvr", f="person"),
                                       update_next = URL(c="dvr", f="person"),
                                       )

            return result
        s3.prep = custom_prep

        return attr

    settings.customise_cr_shelter_registration_controller = customise_cr_shelter_registration_controller

    # -------------------------------------------------------------------------
    # DVR Module Settings and Customizations
    #
    # Uncomment this to enable household size in cases, set to "auto" for automatic counting
    settings.dvr.household_size = "auto"
    # Uncomment this to enable features to manage case flags
    settings.dvr.case_flags = True
    # Case activities use single Needs
    #settings.dvr.case_activity_needs_multiple = True
    # Uncomment this to expose flags to mark appointment types as mandatory
    settings.dvr.mandatory_appointments = True
    # Uncomment this to have appointments with personal presence update last_seen_on
    settings.dvr.appointments_update_last_seen_on = True
    # Uncomment this to have allowance payments update last_seen_on
    settings.dvr.payments_update_last_seen_on = True
    # Uncomment this to automatically update the case status when appointments are completed
    settings.dvr.appointments_update_case_status = True
    # Uncomment this to automatically close appointments when registering certain case events
    settings.dvr.case_events_close_appointments = True
    # Uncomment this to allow cases to belong to multiple case groups ("households")
    #settings.dvr.multiple_case_groups = True
    # Configure a regular expression pattern for ID Codes (QR Codes)
    settings.dvr.id_code_pattern = "(?P<label>[^,]*),(?P<family>[^,]*),(?P<last_name>[^,]*),(?P<first_name>[^,]*),(?P<date_of_birth>[^,]*),.*"
    # Issue a "not checked-in" warning in case event registration
    settings.dvr.event_registration_checkin_warning = True

    # -------------------------------------------------------------------------
    def customise_dvr_home():
        """ Redirect dvr/index to dvr/person?closed=0 """

        from gluon import URL
        from s3 import s3_redirect_default

        s3_redirect_default(URL(f="person", vars={"closed": "0"}))

    settings.customise_dvr_home = customise_dvr_home

    # -------------------------------------------------------------------------
    #def event_overdue(code, interval):
        #"""
            #Get cases (person_ids) for which a certain event is overdue

            #@param code: the event code
            #@param interval: the interval in days
        #"""

        #db = current.db
        #s3db = current.s3db

        #ttable = s3db.dvr_case_event_type
        #ctable = s3db.dvr_case
        #stable = s3db.dvr_case_status
        #etable = s3db.dvr_case_event

        ## Get event type ID
        #query = (ttable.code == code) & \
                #(ttable.deleted != True)
        #row = db(query).select(ttable.id, limitby=(0, 1)).first()
        #if row:
            #type_id = row.id
        #else:
            ## No such event
            #return set()

        ## Determine deadline
        #now = current.request.utcnow
        #then = now - datetime.timedelta(days=interval)

        ## Check only open cases
        #join = stable.on((stable.id == ctable.status_id) & \
                         #(stable.is_closed == False))

        ## Join only events after the deadline
        #left = etable.on((etable.person_id == ctable.person_id) & \
                         #(etable.type_id == type_id) & \
                         #(etable.date != None) & \
                         #(etable.date >= then) & \
                         #(etable.deleted != True))

        ## ...and then select the rows which don't have any
        #query = (ctable.archived == False) & \
                #(ctable.date < then.date()) & \
                #(ctable.deleted == False)
        #rows = db(query).select(ctable.person_id,
                                #left = left,
                                #join = join,
                                #groupby = ctable.person_id,
                                #having = (etable.date.max() == None),
                                #)
        #return set(row.person_id for row in rows)

    # -------------------------------------------------------------------------
    def customise_pr_person_resource(r, tablename):

        s3db = current.s3db
        auth = current.auth

        has_permission = auth.s3_has_permission

        # Users who can not register new residents also have
        # only limited write-access to basic details of residents
        if r.controller == "dvr" and not has_permission("create", "pr_person"):

            # Can not write any fields in main person record
            # (fields in components may still be writable, though)
            ptable = s3db.pr_person
            for field in ptable:
                field.writable = False

            # Can not add or edit contact data in person form
            s3db.configure("pr_contact", insertable=False)

            # Can not update shelter registration from person form
            # - check-in/check-out may still be permitted, however
            # - STAFF can update housing unit

            is_staff = auth.s3_has_role("STAFF")

            rtable = s3db.cr_shelter_registration
            for field in rtable:
                if field.name != "shelter_unit_id" or not is_staff:
                    field.writable = False

    settings.customise_pr_person_resource = customise_pr_person_resource

    # -------------------------------------------------------------------------
    def configure_person_tags():
        """
            Configure filtered pr_person_tag components for
            registration numbers:
                - EasyOpt Number (tag=EONUMBER)
                - BAMF Registration Number (tag=BAMF)
        """

        current.s3db.add_components("pr_person",
                                    pr_person_tag = ({"name": "eo_number",
                                                      "joinby": "person_id",
                                                      "filterby": {
                                                        "tag": "EONUMBER",
                                                        },
                                                      "multiple": False,
                                                      },
                                                     {"name": "bamf",
                                                      "joinby": "person_id",
                                                      "filterby": {
                                                        "tag": "BAMF",
                                                        },
                                                      "multiple": False,
                                                      },
                                                     )
                                    )

    # -------------------------------------------------------------------------
    def customise_pr_person_controller(**attr):

        db = current.db
        s3db = current.s3db
        s3 = current.response.s3

        has_role = current.auth.s3_has_role
        is_admin = has_role(current.auth.get_system_roles().ADMIN)

        # Roles with extended access to person form
        PRIVILEGED = ("ADMIN_HEAD",
                      "ADMINISTRATION",
                      "INFO_POINT",
                      "MEDICAL",
                      "POLICE",
                      "RP",
                      "SECURITY_HEAD",
                      )

        s3.is_privileged = None
        def privileged():
            # Lazy check for privileged access to person form
            privileged = s3.is_privileged
            if privileged is None:
                privileged = is_admin or any(has_role(role) for role in PRIVILEGED)
                s3.is_privileged = privileged
            return privileged

        QUARTIERMANAGER = has_role("QUARTIER") and not privileged()

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            if QUARTIERMANAGER:
                # Enforce closed=0
                r.vars["closed"] = r.get_vars["closed"] = "0"

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            get_vars = r.get_vars

            archived = get_vars.get("archived")
            if archived in ("1", "true", "yes"):
                crud_strings = s3.crud_strings["pr_person"]
                crud_strings["title_list"] = T("Invalid Cases")

            controller = r.controller
            resource = r.resource

            if controller == "security":
                # Restricted view for Security staff
                if r.component:
                    redirect(r.url(method=""))

                # Autocomplete using alternative search method
                search_fields = ("first_name", "last_name", "pe_label")
                s3db.set_method("pr", "person",
                                method = "search_ac",
                                action = s3db.pr_PersonSearchAutocomplete(search_fields),
                                )

                current.deployment_settings.ui.export_formats = None

                # Filter to valid and open cases
                query = (FS("dvr_case.id") != None) & \
                        ((FS("dvr_case.archived") == False) | \
                         (FS("dvr_case.archived") == None)) & \
                        (FS("dvr_case.status_id$is_closed") == False)
                resource.add_filter(query)

                # Adjust CRUD strings
                s3.crud_strings["pr_person"].update(
                    {"title_list": T("Current Cases"),
                     "label_list_button": T("List Cases"),
                     }
                    )

                # No side menu
                current.menu.options = None

                # Only Show Security Notes
                ntable = s3db.dvr_note_type
                note_type = db(ntable.name == "Security").select(ntable.id,
                                                                 limitby=(0, 1),
                                                                 ).first()
                try:
                    note_type_id = note_type.id
                except:
                    current.log.error("Prepop not done - deny access to dvr_note component")
                    note_type_id = None
                    atable = s3db.dvr_note
                    atable.date.readable = atable.date.writable = False
                    atable.note.readable = atable.note.writable = False

                # Custom CRUD form
                from s3 import S3SQLCustomForm, S3SQLInlineComponent
                crud_form = S3SQLCustomForm(
                                (T("ID"), "pe_label"),
                                "last_name",
                                "first_name",
                                "date_of_birth",
                                #"gender",
                                "person_details.nationality",
                                "cr_shelter_registration.shelter_unit_id",
                                S3SQLInlineComponent(
                                        "case_note",
                                        fields = [(T("Date"), "date"),
                                                  "note",
                                                  ],
                                        filterby = {"field": "note_type_id",
                                                    "options": note_type_id,
                                                    },
                                        label = T("Security Notes"),
                                        ),
                                )

                # Custom list fields
                list_fields = [(T("ID"), "pe_label"),
                               "last_name",
                               "first_name",
                               "date_of_birth",
                               #"gender",
                               "person_details.nationality",
                               "shelter_registration.shelter_unit_id",
                               ]

                # Profile page (currently unused)
                if r.method == "profile":
                    from gluon.html import DIV, H2, P, TABLE, TR, TD, A
                    from s3 import s3_fullname
                    person_id = r.id
                    record = r.record
                    table = r.table
                    dtable = s3db.pr_person_details
                    details = db(dtable.person_id == person_id).select(dtable.nationality,
                                                                       limitby=(0, 1)
                                                                       ).first()
                    try:
                        nationality = details.nationality
                    except:
                        nationality = None
                    rtable = s3db.cr_shelter_registration
                    reg = db(rtable.person_id == person_id).select(rtable.shelter_unit_id,
                                                                   limitby=(0, 1)
                                                                   ).first()
                    try:
                        shelter_unit_id = reg.shelter_unit_id
                    except:
                        shelter_unit_id = None
                    profile_header = DIV(H2(s3_fullname(record)),
                                         TABLE(TR(TD(T("ID")),
                                                  TD(record.pe_label)
                                                  ),
                                               TR(TD(table.last_name.label),
                                                  TD(record.last_name)
                                                  ),
                                               TR(TD(table.first_name.label),
                                                  TD(record.first_name)
                                                  ),
                                               TR(TD(table.date_of_birth.label),
                                                  TD(record.date_of_birth)
                                                  ),
                                               TR(TD(dtable.nationality.label),
                                                  TD(nationality)
                                                  ),
                                               TR(TD(rtable.shelter_unit_id.label),
                                                  TD(shelter_unit_id)
                                                  ),
                                               ),
                                         _class="profile-header",
                                         )
                    notes_widget = dict(label = "Security Notes",
                                        label_create = "Add Note",
                                        type = "datatable",
                                        tablename = "dvr_note",
                                        filter = ((FS("note_type_id$name") == "Security") & \
                                                  (FS("person_id") == person_id)),
                                        #icon = "report",
                                        create_controller = "dvr",
                                        create_function = "note",
                                        )
                    profile_widgets = [notes_widget]
                else:
                    profile_header = None
                    profile_widgets = None

                resource.configure(crud_form = crud_form,
                                   list_fields = list_fields,
                                   profile_header = profile_header,
                                   profile_widgets = profile_widgets,
                                   )

            elif controller == "dvr":

                from gluon import Field, IS_EMPTY_OR, IS_IN_SET, IS_NOT_EMPTY

                configure = resource.configure
                table = r.table
                ctable = s3db.dvr_case

                if r.representation in ("html", "iframe", "aadata"):
                    # Delivers HTML, so restrict to GUI:
                    configure(extra_fields = ["shelter_registration.registration_status",
                                              "shelter_registration.check_out_date",
                                              ],
                              )

                if not r.component:

                    configure_person_tags()

                    # Set default shelter for shelter registration
                    shelter_id = drk_default_shelter()
                    if shelter_id:
                        rtable = s3db.cr_shelter_registration
                        field = rtable.shelter_id
                        field.default = shelter_id
                        field.readable = field.writable = False

                        # Filter housing units to units of this shelter
                        field = rtable.shelter_unit_id
                        dbset = db(s3db.cr_shelter_unit.shelter_id == shelter_id)
                        field.requires = IS_EMPTY_OR(IS_ONE_OF(dbset,
                                            "cr_shelter_unit.id",
                                            field.represent,
                                            # Only available units:
                                            filterby = "status",
                                            filter_opts = (1,),
                                            sort=True,
                                            ))

                    default_site = settings.get_org_default_site()
                    default_organisation = settings.get_org_default_organisation()

                    if default_organisation and not default_site:

                        # Limit sites to default_organisation
                        field = ctable.site_id
                        requires = field.requires
                        if requires:
                            if isinstance(requires, IS_EMPTY_OR):
                                requires = requires.other
                            if hasattr(requires, "dbset"):
                                stable = s3db.org_site
                                query = (stable.organisation_id == default_organisation)
                                requires.dbset = db(query)

                    configure = resource.configure
                    if r.interactive and r.method != "import":

                        # Registration status effective dates not manually updateable
                        if r.id:
                            rtable = s3db.cr_shelter_registration
                            field = rtable.check_in_date
                            field.writable = False
                            field.label = T("Last Check-in")
                            field = rtable.check_out_date
                            field.writable = False
                            field.label = T("Last Check-out")

                        # Make marital status mandatory, remove "other"
                        dtable = s3db.pr_person_details
                        field = dtable.marital_status
                        options = dict(s3db.pr_marital_status_opts)
                        del options[9] # Remove "other"
                        field.requires = IS_IN_SET(options, zero=None)

                        # Make gender mandatory, remove "unknown"
                        field = table.gender
                        field.default = None
                        from s3 import IS_PERSON_GENDER
                        options = dict(s3db.pr_gender_opts)
                        del options[1] # Remove "unknown"
                        field.requires = IS_PERSON_GENDER(options, sort = True)

                        # No comment for pe_label
                        field = table.pe_label
                        field.comment = None

                        # Last name is required
                        field = table.last_name
                        field.requires = IS_NOT_EMPTY()

                        # Check whether the shelter registration shall be cancelled
                        cancel = False
                        if r.http == "POST":
                            post_vars = r.post_vars
                            archived = post_vars.get("sub_dvr_case_archived")
                            status_id = post_vars.get("sub_dvr_case_status_id")
                            if archived:
                                cancel = True
                            if not cancel and status_id:
                                stable = s3db.dvr_case_status
                                status = db(stable.id == status_id).select(stable.is_closed,
                                                                           limitby = (0, 1),
                                                                           ).first()
                                try:
                                    if status.is_closed:
                                        cancel = True
                                except:
                                    pass

                        if cancel:
                            # Ignore registration data in form if the registration
                            # is to be cancelled - otherwise a new registration is
                            # created by the subform-processing right after
                            # dvr_case_onaccept deletes the current one:
                            reg_shelter = None
                            reg_status = None
                            reg_unit_id = None
                            reg_check_in_date = None
                            reg_check_out_date = None
                        else:
                            reg_shelter = "cr_shelter_registration.shelter_id"
                            reg_status = (T("Presence"),
                                          "cr_shelter_registration.registration_status",
                                          )
                            reg_unit_id = "cr_shelter_registration.shelter_unit_id"
                            reg_check_in_date = "cr_shelter_registration.check_in_date"
                            reg_check_out_date = "cr_shelter_registration.check_out_date"

                        # Custom CRUD form
                        from s3 import S3SQLCustomForm, S3SQLInlineComponent, S3SQLInlineLink
                        if privileged():
                            # Extended form
                            crud_form = S3SQLCustomForm(

                                    # Case Details ----------------------------
                                    (T("Case Status"), "dvr_case.status_id"),
                                    S3SQLInlineLink("case_flag",
                                                    label = T("Flags"),
                                                    field = "flag_id",
                                                    help_field = "comments",
                                                    cols = 4,
                                                    ),

                                    # Person Details --------------------------
                                    (T("ID"), "pe_label"),
                                    "last_name",
                                    "first_name",
                                    "person_details.nationality",
                                    "date_of_birth",
                                    "gender",
                                    "person_details.marital_status",

                                    # Process Data ----------------------------
                                    # Will always default & be hidden
                                    "dvr_case.organisation_id",
                                    # Will always default & be hidden
                                    "dvr_case.site_id",
                                    (T("BFV Arrival"), "dvr_case.date"),
                                    "dvr_case.origin_site_id",
                                    "dvr_case.destination_site_id",
                                    S3SQLInlineComponent(
                                            "eo_number",
                                            fields = [("", "value"),
                                                      ],
                                            filterby = {"field": "tag",
                                                        "options": "EONUMBER",
                                                        },
                                            label = T("EasyOpt Number"),
                                            multiple = False,
                                            name = "eo_number",
                                            ),
                                    S3SQLInlineComponent(
                                            "bamf",
                                            fields = [("", "value"),
                                                      ],
                                            filterby = {"field": "tag",
                                                        "options": "BAMF",
                                                        },
                                            label = T("BAMF Reference Number"),
                                            multiple = False,
                                            name = "bamf",
                                            ),
                                    "dvr_case.valid_until",
                                    "dvr_case.stay_permit_until",

                                    # Shelter Data ----------------------------
                                    # Will always default & be hidden
                                    #"cr_shelter_registration.site_id",
                                    reg_shelter,
                                    # @ ToDo: Automate this from the Case Status?
                                    reg_unit_id,
                                    reg_status,
                                    reg_check_in_date,
                                    reg_check_out_date,

                                    # Other Details ---------------------------
                                    "person_details.occupation",
                                    S3SQLInlineComponent(
                                            "contact",
                                            fields = [("", "value"),
                                                        ],
                                            filterby = {"field": "contact_method",
                                                        "options": "SMS",
                                                        },
                                            label = T("Mobile Phone"),
                                            multiple = False,
                                            name = "phone",
                                            ),
                                    "person_details.literacy",
                                    S3SQLInlineComponent(
                                            "case_language",
                                            fields = ["language",
                                                      "quality",
                                                      "comments",
                                                      ],
                                            label = T("Language / Communication Mode"),
                                            ),
                                    "dvr_case.comments",

                                    # Archived-flag ---------------------------
                                    (T("Invalid"), "dvr_case.archived"),
                                    )
                        else:
                            # Reduced form
                            crud_form = S3SQLCustomForm(
                                    S3SQLInlineLink("case_flag",
                                                    label = T("Flags"),
                                                    field = "flag_id",
                                                    help_field = "comments",
                                                    cols = 4,
                                                    ),
                                    (T("ID"), "pe_label"),
                                    "last_name",
                                    "first_name",
                                    "person_details.nationality",
                                    "date_of_birth",
                                    "gender",
                                    reg_unit_id,
                                    S3SQLInlineComponent(
                                            "contact",
                                            fields = [("", "value"),
                                                        ],
                                            filterby = {"field": "contact_method",
                                                        "options": "SMS",
                                                        },
                                            label = T("Mobile Phone"),
                                            multiple = False,
                                            name = "phone",
                                            ),
                                    "dvr_case.comments",
                                    )

                        configure(crud_form = crud_form,
                                  )

                        # Reconfigure filter widgets
                        filter_widgets = resource.get_config("filter_widgets")
                        if filter_widgets:

                            from s3 import S3DateFilter, \
                                           S3OptionsFilter, \
                                           S3TextFilter
                            extend_text_filter = True
                            for fw in filter_widgets:
                                # No filter default for case status
                                if fw.field == "dvr_case.status_id":
                                    fw.opts.default = None
                                if fw.field == "case_flag_case.flag_id":
                                    fw.opts.size = None
                                # Text filter includes EasyOpt Number and Case Comments
                                if extend_text_filter and isinstance(fw, S3TextFilter):
                                    fw.field.extend(("eo_number.value",
                                                     "dvr_case.comments",
                                                     ))
                                    fw.opts.comment = T("You can search by name, ID, EasyOpt number and comments")
                                    extend_text_filter = False

                            # Add filter for date of birth
                            dob_filter = S3DateFilter("date_of_birth")
                            #dob_filter.operator = ["eq"]
                            filter_widgets.insert(1, dob_filter)

                            # Additional filters for privileged roles
                            if privileged():
                                # Add filter for registration date
                                reg_filter = S3DateFilter("dvr_case.date",
                                                          hidden = True,
                                                          )
                                filter_widgets.append(reg_filter)

                                # Add filter for registration status
                                reg_filter = S3OptionsFilter("shelter_registration.registration_status",
                                                             label = T("Presence"),
                                                             options = s3db.cr_shelter_registration_status_opts,
                                                             hidden = True,
                                                             cols = 3,
                                                             )
                                filter_widgets.append(reg_filter)

                                # Add filter for BAMF Registration Number
                                bamf_filter = S3TextFilter(["bamf.value"],
                                                           label = T("BAMF Ref.No."),
                                                           hidden = True,
                                                           )
                                filter_widgets.append(bamf_filter)

                            # Add filter for IDs
                            id_filter = S3TextFilter(["pe_label"],
                                                     label = T("IDs"),
                                                     match_any = True,
                                                     hidden = True,
                                                     comment = T("Search for multiple IDs (separated by blanks)"),
                                                     )
                            filter_widgets.append(id_filter)

                    # Custom list fields (must be outside of r.interactive)
                    list_fields = [(T("ID"), "pe_label"),
                                   #(T("EasyOpt No."), "eo_number.value"),
                                   "last_name",
                                   "first_name",
                                   "date_of_birth",
                                   "gender",
                                   "person_details.nationality",
                                   #"dvr_case.date",
                                   #"dvr_case.status_id",
                                   (T("Shelter"), "shelter_registration.shelter_unit_id"),
                                   ]

                    if privileged():
                        # Additional list fields for privileged roles
                        list_fields.insert(1, (T("EasyOpt No."), "eo_number.value"))
                        list_fields[-1:-1] = ("dvr_case.date",
                                              "dvr_case.status_id",
                                              )

                    if r.representation == "xls":
                        # Extra list_fields for XLS export

                        # Add appointment dates
                        atypes = ["GU",
                                  "X-Ray",
                                  "Sent to RP",
                                  ]
                        COMPLETED = 4
                        afields = []
                        attable = s3db.dvr_case_appointment_type
                        query = attable.name.belongs(atypes)
                        rows = db(query).select(attable.id,
                                                attable.name,
                                                )
                        add_components = s3db.add_components
                        for row in rows:
                            type_id = row.id
                            name = "appointment%s" % type_id
                            hook = {"name": name,
                                    "joinby": "person_id",
                                    "filterby": {"type_id": type_id,
                                                 "status": COMPLETED,
                                                 },
                                    }
                            add_components("pr_person",
                                           dvr_case_appointment = hook,
                                           )
                            afields.append((T(row.name), "%s.date" % name))

                        list_fields.extend(afields)

                        # Add family key
                        s3db.add_components("pr_person",
                                            pr_group = {"name": "family",
                                                        "link": "pr_group_membership",
                                                        "joinby": "person_id",
                                                        "key": "group_id",
                                                        "filterby": {
                                                            "group_type": 7,
                                                            },
                                                        },
                                            )

                        list_fields += [# Current check-in/check-out status
                                        (T("Registration Status"),
                                         "shelter_registration.registration_status",
                                         ),
                                        # Last Check-in date
                                        "shelter_registration.check_in_date",
                                        # Last Check-out date
                                        "shelter_registration.check_out_date",
                                        # Person UUID
                                        ("UUID", "uuid"),
                                        # Family Record ID
                                        (T("Family ID"), "family.id"),
                                        ]
                    configure(list_fields = list_fields)

                elif r.component_name == "case_appointment":

                    # Make appointments tab read-only even if the user is
                    # permitted to create or update appointments (via event
                    # registration), except for ADMINISTRATION/ADMIN_HEAD:
                    if not has_role("ADMINISTRATION") and \
                       not has_role("ADMIN_HEAD"):
                        r.component.configure(insertable = False,
                                              editable = False,
                                              deletable = False,
                                              )
            return result
        s3.prep = custom_prep

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            if QUARTIERMANAGER:
                # Add Action Button to assign Housing Unit to the Resident
                from gluon import URL
                s3.actions = [dict(label=s3_str(T("Assign Shelter")),
                                    _class="action-btn",
                                    url=URL(c="cr",
                                            f="shelter_registration",
                                            args=["assign"],
                                            vars={"person_id": "[id]"},
                                            )),
                               ]

            return output
        s3.postp = custom_postp

        # Custom rheader tabs
        if current.request.controller == "dvr":
            attr = dict(attr)
            attr["rheader"] = drk_dvr_rheader

        return attr

    settings.customise_pr_person_controller = customise_pr_person_controller

    # -------------------------------------------------------------------------
    def customise_pr_group_membership_controller(**attr):

        s3db = current.s3db
        s3 = current.response.s3

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            ROLE = T("Role")

            resource = r.resource
            if r.controller == "dvr":

                # Set default shelter
                shelter_id = drk_default_shelter()
                if shelter_id:
                    rtable = s3db.cr_shelter_registration
                    field = rtable.shelter_id
                    field.default = shelter_id

                if r.interactive:
                    table = resource.table

                    from gluon import IS_EMPTY_OR
                    from s3 import IS_ADD_PERSON_WIDGET2, S3AddPersonWidget2

                    field = table.person_id
                    field.represent = s3db.pr_PersonRepresent(show_link=True)
                    field.requires = IS_ADD_PERSON_WIDGET2()
                    field.widget = S3AddPersonWidget2(controller="dvr")

                    field = table.role_id
                    field.readable = field.writable = True
                    field.label = ROLE
                    field.comment = None
                    field.requires = IS_EMPTY_OR(
                                        IS_ONE_OF(current.db, "pr_group_member_role.id",
                                                  field.represent,
                                                  filterby = "group_type",
                                                  filter_opts = (7,),
                                                  ))

                    field = table.group_head
                    field.label = T("Head of Family")

                    # Custom CRUD strings for this perspective
                    s3.crud_strings["pr_group_membership"] = Storage(
                        label_create = T("Add Family Member"),
                        title_display = T("Family Member Details"),
                        title_list = T("Family Members"),
                        title_update = T("Edit Family Member"),
                        label_list_button = T("List Family Members"),
                        label_delete_button = T("Remove Family Member"),
                        msg_record_created = T("Family Member added"),
                        msg_record_modified = T("Family Member updated"),
                        msg_record_deleted = T("Family Member removed"),
                        msg_list_empty = T("No Family Members currently registered")
                        )

                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id",
                               "person_id$date_of_birth",
                               "person_id$gender",
                               "group_head",
                               (ROLE, "role_id"),
                               (T("Case Status"), "person_id$dvr_case.status_id"),
                               ]
                # Retain group_id in list_fields if added in standard prep
                lfields = resource.get_config("list_fields")
                if "group_id" in lfields:
                    list_fields.insert(0, "group_id")
                resource.configure(filter_widgets = None,
                                   list_fields = list_fields,
                                   )
            return result
        s3.prep = custom_prep

        attr["rheader"] = drk_dvr_rheader

        return attr

    settings.customise_pr_group_membership_controller = customise_pr_group_membership_controller

    # -------------------------------------------------------------------------
    def dvr_case_onaccept(form):
        """
            If case is archived or closed then remove shelter_registration,
            otherwise ensure that a shelter_registration exists for any
            open and valid case
        """

        db = current.db
        s3db = current.s3db

        form_vars = form.vars
        archived = form_vars.archived
        person_id = form_vars.person_id

        # Inline shelter registration?
        inline = "sub_shelter_registration_registration_status" in \
                 current.request.post_vars

        cancel = False

        if archived:
            cancel = True

        else:
            status_id = form_vars.status_id
            if status_id:

                stable = s3db.dvr_case_status
                status = db(stable.id == status_id).select(stable.is_closed,
                                                           limitby = (0, 1)
                                                           ).first()
                try:
                    if status.is_closed:
                        cancel = True
                except:
                    current.log.error("Status %s not found" % status_id)
                    return

        rtable = s3db.cr_shelter_registration
        query = (rtable.person_id == person_id)

        if cancel:
            reg = db(query).select(rtable.id, limitby=(0, 1)).first()
            if reg:
                resource = s3db.resource("cr_shelter_registration",
                                         id = reg.id,
                                         )
                resource.delete()

        elif not inline:
            # We're called without inline shelter registration, so
            # make sure there is a shelter registration if the case
            # is valid and open:
            reg = db(query).select(rtable.id, limitby=(0, 1)).first()
            if not reg:
                if rtable.shelter_id.default is not None:
                    # Create default shelter registration
                    rtable.insert(person_id=person_id)
                else:
                    current.response.warning = T("Person could not be registered to a shelter, please complete case manually")

    # -------------------------------------------------------------------------
    def customise_dvr_case_resource(r, tablename):

        s3db = current.s3db

        config = {}
        get_config = s3db.get_config

        for method in ("create", "update", None):

            setting = "%s_onaccept" % method if method else "onaccept"
            default = get_config(tablename, setting)
            if not default:
                if method is None and len(config) < 2:
                    onaccept = dvr_case_onaccept
                else:
                    continue
            elif not isinstance(default, list):
                onaccept = [default, dvr_case_onaccept]
            else:
                onaccept = default
                if all(cb != dvr_case_onaccept for cb in onaccept):
                    onaccept.append(dvr_case_onaccept)
            config[setting] = onaccept

        s3db.configure(tablename, **config)

        ctable = s3db.dvr_case

        # Expose expiration dates
        field = ctable.valid_until
        field.label = T("BÜMA valid until")
        field.readable = field.writable = True
        field = ctable.stay_permit_until
        field.readable = field.writable = True

        # Set all fields read-only except comments, unless
        # the user has permission to create cases
        if not current.auth.s3_has_permission("create", "dvr_case"):
            for field in ctable:
                if field.name != "comments":
                    field.writable = False

    settings.customise_dvr_case_resource = customise_dvr_case_resource

    # -------------------------------------------------------------------------
    def dvr_note_onaccept(form):
        """
            Set owned_by_group
        """

        db = current.db
        s3db = current.s3db
        form_vars = form.vars
        table = s3db.dvr_note_type
        types = db(table.name.belongs(("Medical", "Security"))).select(table.id,
                                                                       table.name).as_dict(key="name")
        try:
            MEDICAL = types["Medical"]["id"]
        except:
            current.log.error("Prepop not completed...cannot assign owned_by_group to dvr_note_type")
            return
        SECURITY = types["Security"]["id"]
        note_type_id = form_vars.note_type_id
        if note_type_id == str(MEDICAL):
            table = s3db.dvr_note
            gtable = db.auth_group
            role = db(gtable.uuid == "MEDICAL").select(gtable.id,
                                                       limitby=(0, 1)
                                                       ).first()
            try:
                group_id = role.id
            except:
                current.log.error("Prepop not completed...cannot assign owned_by_group to dvr_note")
                return
            db(table.id == form_vars.id).update(owned_by_group=group_id)
        elif note_type_id == str(SECURITY):
            table = s3db.dvr_note
            gtable = db.auth_group
            role = db(gtable.uuid == "SECURITY").select(gtable.id,
                                                        limitby=(0, 1)
                                                        ).first()
            try:
                group_id = role.id
            except:
                current.log.error("Prepop not completed...cannot assign owned_by_group to dvr_note")
                return
            db(table.id == form_vars.id).update(owned_by_group=group_id)

    # -------------------------------------------------------------------------
    def customise_dvr_note_resource(r, tablename):

        auth = current.auth

        if not auth.s3_has_role("ADMIN"):

            # Restrict access by note type
            GENERAL = "General"
            MEDICAL = "Medical"
            SECURITY = "Security"

            permitted_note_types = [GENERAL]

            user = auth.user
            if user:
                # Roles permitted to access "Security" type notes
                SECURITY_ROLES = ("ADMIN_HEAD",
                                  "SECURITY_HEAD",
                                  "POLICE",
                                  "MEDICAL",
                                  )

                # Roles permitted to access "Health" type notes
                MEDICAL_ROLES = ("ADMIN_HEAD",
                                 "MEDICAL",
                                 )

                # Get role IDs
                db = current.db
                s3db = current.s3db
                gtable = s3db.auth_group
                roles = db(gtable.deleted != True).select(gtable.uuid,
                                                          gtable.id,
                                                          ).as_dict(key = "uuid")

                realms = user.realms

                security_roles = (roles[uuid]["id"]
                                  for uuid in SECURITY_ROLES if uuid in roles)
                if any(role in realms for role in security_roles):
                    permitted_note_types.append(SECURITY)

                medical_roles = (roles[uuid]["id"]
                                 for uuid in MEDICAL_ROLES if uuid in roles)
                if any(role in realms for role in medical_roles):
                    permitted_note_types.append(MEDICAL)

            # Filter notes to permitted note types
            query = FS("note_type_id$name").belongs(permitted_note_types)
            if r.tablename == "dvr_note":
                r.resource.add_filter(query)
            else:
                r.resource.add_component_filter("case_note", query)

            # Filter note type selector to permitted note types
            ttable = s3db.dvr_note_type
            query = ttable.name.belongs(permitted_note_types)
            rows = db(query).select(ttable.id)
            note_type_ids = [row.id for row in rows]

            table = s3db.dvr_note
            field = table.note_type_id
            field.label = T("Category")

            if len(note_type_ids) == 1:
                field.default = note_type_ids[0]
                field.writable = False

            field.requires = IS_ONE_OF(db(query), "dvr_note_type.id",
                                       field.represent,
                                       )

    settings.customise_dvr_note_resource = customise_dvr_note_resource

    # -------------------------------------------------------------------------
    def customise_dvr_case_activity_resource(r, tablename):

        if not current.auth.s3_has_role("MEDICAL"):

            s3db = current.s3db
            from gluon import IS_EMPTY_OR

            HEALTH = "Health"

            # Remove "Health" need type from need_id options widget
            ntable = s3db.dvr_need
            dbset = current.db(ntable.name != HEALTH)

            table = s3db.dvr_case_activity
            field = table.need_id
            field.requires = IS_EMPTY_OR(IS_ONE_OF(dbset, "dvr_need.id",
                                                   field.represent,
                                                   ))

            # Hide activities for need type "Health"
            query = (FS("need_id$name") != HEALTH)

            if r.tablename == "dvr_case_activity":
                r.resource.add_filter(query)

                # @todo: remove "Health" need type from need_id filter widget

            elif r.component and r.component.tablename == "dvr_case_activity":
                r.component.add_filter(query)

    settings.customise_dvr_case_activity_resource = customise_dvr_case_activity_resource

    # -------------------------------------------------------------------------
    def customise_dvr_case_activity_controller(**attr):

        s3db = current.s3db
        s3 = current.response.s3

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            resource = r.resource

            # Filter to active cases
            if not r.record:
                query = (FS("person_id$dvr_case.archived") == False) | \
                        (FS("person_id$dvr_case.archived") == None)
                resource.add_filter(query)

            if not r.component:

                filter_widgets = resource.get_config("filter_widgets")
                if filter_widgets:

                    configure_person_tags()

                    from s3 import S3TextFilter
                    for fw in filter_widgets:
                        if isinstance(fw, S3TextFilter):
                            fw.field.append("person_id$eo_number.value")
                            break

                # Custom list fields
                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id$first_name",
                               "person_id$last_name",
                               "need_id",
                               "need_details",
                               "emergency",
                               "activity_details",
                               "followup",
                               "followup_date",
                               "completed",
                               ]

                r.resource.configure(list_fields = list_fields,
                                    )

            return result
        s3.prep = custom_prep

        return attr

    settings.customise_dvr_case_activity_controller = customise_dvr_case_activity_controller

    # -------------------------------------------------------------------------
    def customise_dvr_case_appointment_controller(**attr):

        s3 = current.response.s3
        s3db = current.s3db

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            resource = r.resource

            # Filter to active cases
            if not r.record:
                query = (FS("person_id$dvr_case.archived") == False) | \
                        (FS("person_id$dvr_case.archived") == None)
                resource.add_filter(query)

            if not r.component:

                configure_person_tags()

                if r.interactive and not r.id:

                    # Custom filter widgets
                    from s3 import S3TextFilter, S3OptionsFilter, S3DateFilter, s3_get_filter_opts
                    filter_widgets = [
                        S3TextFilter(["person_id$pe_label",
                                      "person_id$first_name",
                                      "person_id$last_name",
                                      "person_id$eo_number.value",
                                      ],
                                      label = T("Search"),
                                      ),
                        S3OptionsFilter("type_id",
                                        options = s3_get_filter_opts("dvr_case_appointment_type",
                                                                     translate = True,
                                                                     ),
                                        cols = 3,
                                        ),
                        S3OptionsFilter("status",
                                        options = s3db.dvr_appointment_status_opts,
                                        default = 2,
                                        ),
                        S3DateFilter("date",
                                     ),
                        S3OptionsFilter("person_id$dvr_case.status_id$is_closed",
                                        cols = 2,
                                        default = False,
                                        #hidden = True,
                                        label = T("Case Closed"),
                                        options = {True: T("Yes"),
                                                   False: T("No"),
                                                   },
                                        ),
                        S3TextFilter(["person_id$pe_label"],
                                     label = T("IDs"),
                                     match_any = True,
                                     hidden = True,
                                     comment = T("Search for multiple IDs (separated by blanks)"),
                                     ),
                        ]

                    resource.configure(filter_widgets = filter_widgets)

                # Default filter today's and tomorrow's appointments
                from s3 import s3_set_default_filter
                now = r.utcnow
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow = today + datetime.timedelta(days=1)
                s3_set_default_filter("~.date",
                                      {"ge": today, "le": tomorrow},
                                      tablename = "dvr_case_appointment",
                                      )

                # Field Visibility
                table = resource.table
                field = table.case_id
                field.readable = field.writable = False

                # Custom list fields
                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id$first_name",
                               "person_id$last_name",
                               "type_id",
                               "date",
                               "status",
                               "comments",
                               ]

                if r.representation == "xls":
                    # Include Person UUID
                    list_fields.append(("UUID", "person_id$uuid"))

                resource.configure(list_fields = list_fields,
                                   insertable = False,
                                   deletable = False,
                                   update_next = r.url(method=""),
                                   )

            return result
        s3.prep = custom_prep

        return attr

    settings.customise_dvr_case_appointment_controller = customise_dvr_case_appointment_controller

    # -------------------------------------------------------------------------
    def customise_dvr_allowance_controller(**attr):

        s3 = current.response.s3
        s3db = current.s3db

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            resource = r.resource

            # Filter to active cases
            if not r.record:
                query = (FS("person_id$dvr_case.archived") == False) | \
                        (FS("person_id$dvr_case.archived") == None)
                resource.add_filter(query)

            if not r.component:

                if r.interactive and not r.id:
                    # Custom filter widgets
                    from s3 import S3TextFilter, \
                                   S3OptionsFilter, \
                                   S3DateFilter

                    filter_widgets = [
                        S3TextFilter(["person_id$pe_label",
                                      "person_id$first_name",
                                      "person_id$middle_name",
                                      "person_id$last_name",
                                      ],
                                      label = T("Search"),
                                      ),
                        S3OptionsFilter("status",
                                        default = 1,
                                        cols = 4,
                                        options = s3db.dvr_allowance_status_opts,
                                        ),
                        S3DateFilter("date"),
                        S3DateFilter("paid_on"),
                        S3DateFilter("entitlement_period",
                                     hidden = True,
                                     )
                        ]
                    resource.configure(filter_widgets = filter_widgets)

                # Field Visibility
                table = resource.table
                field = table.case_id
                field.readable = field.writable = False

                # Can't change beneficiary
                field = table.person_id
                field.writable = False

                # Custom list fields
                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id",
                               "entitlement_period",
                               "date",
                               "currency",
                               "amount",
                               "status",
                               "paid_on",
                               "comments",
                               ]
                if r.representation == "xls":
                    list_fields.append(("UUID", "person_id$uuid"))

                resource.configure(list_fields = list_fields,
                                   insertable = False,
                                   deletable = False,
                                   #editable = False,
                                   )

            return result
        s3.prep = custom_prep

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            if r.method == "register":
                from s3 import S3CustomController
                S3CustomController._view("DRK", "register_case_event.html")
            return output
        s3.postp = custom_postp

        return attr

    settings.customise_dvr_allowance_controller = customise_dvr_allowance_controller

    # -------------------------------------------------------------------------
    def case_event_create_onaccept(form):
        """
            Custom onaccept-method for case events
                - cascade FOOD events to other members of the same case group

            @param form: the Form
        """

        # Get form.vars.id
        formvars = form.vars
        try:
            record_id = formvars.id
        except AttributeError:
            record_id = None
        if not record_id:
            return

        # Prevent recursion
        try:
            if formvars._cascade:
                return
        except AttributeError:
            pass

        db = current.db
        s3db = current.s3db

        # Get the person ID and event type code and interval
        ttable = s3db.dvr_case_event_type
        etable = s3db.dvr_case_event
        query = (etable.id == record_id) & \
                (ttable.id == etable.type_id)
        row = db(query).select(etable.person_id,
                               etable.type_id,
                               etable.date,
                               ttable.code,
                               ttable.min_interval,
                               limitby = (0, 1),
                               ).first()
        if not row:
            return

        # Extract the event attributes
        event = row.dvr_case_event
        person_id = event.person_id
        event_type_id = event.type_id
        event_date = event.date

        # Extract the event type attributes
        event_type = row.dvr_case_event_type
        event_code = event_type.code
        interval = event_type.min_interval

        if event_code == "FOOD":

            gtable = s3db.pr_group
            mtable = s3db.pr_group_membership
            ctable = s3db.dvr_case
            stable = s3db.dvr_case_status

            # Get all case groups this person belongs to
            query = ((mtable.person_id == person_id) & \
                    (mtable.deleted != True) & \
                    (gtable.id == mtable.group_id) & \
                    (gtable.group_type == 7))
            rows = db(query).select(gtable.id)
            group_ids = set(row.id for row in rows)

            # Find all other members of these case groups, and
            # the last FOOD event registration date/time for each
            members = {}
            if group_ids:
                left = [ctable.on(ctable.person_id == mtable.person_id),
                        stable.on(stable.id == ctable.status_id),
                        etable.on((etable.person_id == mtable.person_id) & \
                                  (etable.type_id == event_type_id) & \
                                  (etable.deleted != True)),
                        ]
                query = (mtable.person_id != person_id) & \
                        (mtable.group_id.belongs(group_ids)) & \
                        (mtable.deleted != True) & \
                        (ctable.archived != True) & \
                        (ctable.deleted != True) & \
                        (stable.is_closed != True)
                latest = etable.date.max()
                case_id = ctable._id.min()
                rows = db(query).select(mtable.person_id,
                                        case_id,
                                        latest,
                                        left = left,
                                        groupby = mtable.person_id,
                                        )
                for row in rows:
                    person = row[mtable.person_id]
                    if person not in members:
                        members[person] = (row[case_id], row[latest])

            # For each case group member, replicate the event
            now = current.request.utcnow
            for member, details in members.items():

                case_id, latest = details

                # Check minimum waiting interval
                passed = True
                if interval and latest:
                    earliest = latest + datetime.timedelta(hours=interval)
                    if earliest > now:
                        passed = False
                if not passed:
                    continue

                # Replicate the event for this member
                data = {"person_id": member,
                        "case_id": case_id,
                        "type_id": event_type_id,
                        "date": event_date,
                        }
                event_id = etable.insert(**data)
                if event_id:
                    # Set record owner
                    auth = current.auth
                    auth.s3_set_record_owner(etable, event_id)
                    auth.s3_make_session_owner(etable, event_id)
                    # Execute onaccept
                    # => set _cascade flag to prevent recursion
                    data["id"] = event_id
                    data["_cascade"] = True
                    s3db.onaccept(etable, data, method="create")

    # -------------------------------------------------------------------------
    def customise_dvr_case_event_resource(r, tablename):

        resource = current.s3db.resource("dvr_case_event")

        # Get the current create_onaccept setting
        hook = "create_onaccept"
        callback = resource.get_config(hook)

        # Fall back to generic onaccept
        if not callback:
            hook = "onaccept"
            callback = resource.get_config(hook)

        # Extend with custom onaccept
        custom_onaccept = case_event_create_onaccept
        if callback:
            if isinstance(callback, (tuple, list)):
                if custom_onaccept not in callback:
                    callback = list(callback) + [custom_onaccept]
            else:
                callback = [callback, custom_onaccept]
        else:
            callback = custom_onaccept
        resource.configure(**{hook: callback})

    settings.customise_dvr_case_event_resource = customise_dvr_case_event_resource

    # -------------------------------------------------------------------------
    def customise_dvr_case_event_controller(**attr):

        s3 = current.response.s3

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            if r.method == "register":
                from s3 import S3CustomController
                S3CustomController._view("DRK", "register_case_event.html")
            return output
        s3.postp = custom_postp

        return attr

    settings.customise_dvr_case_event_controller = customise_dvr_case_event_controller

    # -------------------------------------------------------------------------
    def customise_org_facility_resource(r, tablename):

        s3db = current.s3db

        # Hide "code" field (not needed)
        table = s3db.org_facility
        field = table.code
        field.readable = field.writable = False

        # Location selector just needs country + address
        from s3 import S3LocationSelector
        field = table.location_id
        field.widget = S3LocationSelector(levels = ["L0"],
                                          show_address=True,
                                          show_map = False,
                                          )

        field = table.obsolete
        field.label = T("Inactive")
        field.represent = lambda opt: T("Inactive") if opt else current.messages["NONE"]

        # Custom list fields
        list_fields = ["name",
                       "site_facility_type.facility_type_id",
                       "organisation_id",
                       "location_id",
                       "contact",
                       "phone1",
                       "phone2",
                       "email",
                       #"website",
                       "obsolete",
                       "comments",
                       ]

        # Custom filter widgets
        from s3 import S3TextFilter, S3OptionsFilter, s3_get_filter_opts
        filter_widgets = [S3TextFilter(["name",
                                        "organisation_id$name",
                                        "organisation_id$acronym",
                                        "comments",
                                        ],
                                        label = T("Search"),
                                       ),
                          S3OptionsFilter("site_facility_type.facility_type_id",
                                          options = s3_get_filter_opts("org_facility_type",
                                                                       translate = True,
                                                                       ),
                                          ),
                          S3OptionsFilter("organisation_id",
                                          ),
                          S3OptionsFilter("obsolete",
                                          options = {False: T("No"),
                                                     True: T("Yes"),
                                                     },
                                          default = [False],
                                          cols = 2,
                                          )
                          ]

        s3db.configure("org_facility",
                       #deletable = False,
                       filter_widgets = filter_widgets,
                       list_fields = list_fields,
                       )

    settings.customise_org_facility_resource = customise_org_facility_resource

    # -------------------------------------------------------------------------
    def customise_org_facility_controller(**attr):

        # Allow selection of all countries
        current.deployment_settings.gis.countries = []

        # Custom rheader+tabs
        if current.request.controller == "org":
            attr = dict(attr)
            attr["rheader"] = drk_org_rheader

        return attr

    settings.customise_org_facility_controller = customise_org_facility_controller

    # -------------------------------------------------------------------------
    def customise_project_task_resource(r, tablename):
        """
            Restrict list of assignees to just Staff/Volunteers
        """

        db = current.db
        s3db = current.s3db

        # Configure custom form for tasks
        from s3 import S3SQLCustomForm, S3SQLInlineLink
        crud_form = S3SQLCustomForm("name",
                                    "status",
                                    "priority",
                                    "description",
                                    "source",
                                    S3SQLInlineLink("shelter_inspection_flag",
                                                    field="inspection_flag_id",
                                                    label=T("Shelter Inspection"),
                                                    readonly=True,
                                                    render_list=True,
                                                    ),
                                    "pe_id",
                                    "date_due",
                                    )
        s3db.configure("project_task",
                       crud_form = crud_form,
                       )

        # Filter assignees to human resources
        htable = s3db.hrm_human_resource
        ptable = s3db.pr_person
        query = (htable.deleted == False) & \
                (htable.person_id == ptable.id)
        rows = db(query).select(ptable.pe_id)
        pe_ids = set(row.pe_id for row in rows)

        # ...and teams
        gtable = s3db.pr_group
        query = (gtable.group_type == 3) & \
                (gtable.deleted == False)
        rows = db(query).select(gtable.pe_id)
        pe_ids |= set(row.pe_id for row in rows)

        from gluon import IS_EMPTY_OR
        s3db.project_task.pe_id.requires = IS_EMPTY_OR(
            IS_ONE_OF(db, "pr_pentity.pe_id",
                      s3db.pr_PersonEntityRepresent(show_label = False,
                                                    show_type = True,
                                                    ),
                      sort = True,
                      filterby = "pe_id",
                      filter_opts = pe_ids,
                      ))

    settings.customise_project_task_resource = customise_project_task_resource

    # -------------------------------------------------------------------------
    # Comment/uncomment modules here to disable/enable them
    # Modules menu is defined in modules/eden/menu.py
    settings.modules = OrderedDict([
        # Core modules which shouldn't be disabled
        ("default", Storage(
            name_nice = T("Home"),
            restricted = False, # Use ACLs to control access to this module
            access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
            module_type = None  # This item is not shown in the menu
        )),
        ("admin", Storage(
            name_nice = T("Administration"),
            #description = "Site Administration",
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
            module_type = None  # This item is handled separately for the menu
        )),
        ("appadmin", Storage(
            name_nice = T("Administration"),
            #description = "Site Administration",
            restricted = True,
            module_type = None  # No Menu
        )),
        ("errors", Storage(
            name_nice = T("Ticket Viewer"),
            #description = "Needed for Breadcrumbs",
            restricted = False,
            module_type = None  # No Menu
        )),
        #("sync", Storage(
        #    name_nice = T("Synchronization"),
        #    #description = "Synchronization",
        #    restricted = True,
        #    access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
        #    module_type = None  # This item is handled separately for the menu
        #)),
        #("tour", Storage(
        #    name_nice = T("Guided Tour Functionality"),
        #    module_type = None,
        #)),
        #("translate", Storage(
        #    name_nice = T("Translation Functionality"),
        #    #description = "Selective translation of strings based on module.",
        #    module_type = None,
        #)),
        ("gis", Storage(
            name_nice = T("Map"),
            #description = "Situation Awareness & Geospatial Analysis",
            restricted = True,
            module_type = 6,     # 6th item in the menu
        )),
        ("pr", Storage(
            name_nice = T("Person Registry"),
            #description = "Central point to record details on People",
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
            module_type = 10
        )),
        ("org", Storage(
            name_nice = T("Organizations"),
            #description = 'Lists "who is doing what & where". Allows relief agencies to coordinate their activities',
            restricted = True,
            module_type = 1
        )),
        ("hrm", Storage(
           name_nice = T("Staff"),
           #description = "Human Resources Management",
           restricted = True,
           module_type = 2,
        )),
        ("vol", Storage(
           name_nice = T("Volunteers"),
           #description = "Human Resources Management",
           restricted = True,
           module_type = 2,
        )),
        ("cms", Storage(
         name_nice = T("Content Management"),
        #description = "Content Management System",
         restricted = True,
         module_type = 10,
        )),
        ("doc", Storage(
           name_nice = T("Documents"),
           #description = "A library of digital resources, such as photos, documents and reports",
           restricted = True,
           module_type = 10,
        )),
        ("msg", Storage(
           name_nice = T("Messaging"),
           #description = "Sends & Receives Alerts via Email & SMS",
           restricted = True,
           # The user-visible functionality of this module isn't normally required. Rather it's main purpose is to be accessed from other modules.
           module_type = None,
        )),
        ("supply", Storage(
           name_nice = T("Supply Chain Management"),
           #description = "Used within Inventory Management, Request Management and Asset Management",
           restricted = True,
           module_type = None, # Not displayed
        )),
        ("inv", Storage(
           name_nice = T("Warehouses"),
           #description = "Receiving and Sending Items",
           restricted = True,
           module_type = 4
        )),
        ("asset", Storage(
           name_nice = T("Assets"),
           #description = "Recording and Assigning Assets",
           restricted = True,
           module_type = 5,
        )),
        # Vehicle depends on Assets
        #("vehicle", Storage(
        #    name_nice = T("Vehicles"),
        #    #description = "Manage Vehicles",
        #    restricted = True,
        #    module_type = 10,
        #)),
        ("req", Storage(
           name_nice = T("Requests"),
           #description = "Manage requests for supplies, assets, staff or other resources. Matches against Inventories where supplies are requested.",
           restricted = True,
           module_type = 10,
        )),
        ("project", Storage(
           name_nice = T("Projects"),
           #description = "Tracking of Projects, Activities and Tasks",
           restricted = True,
           module_type = 2
        )),
        ("cr", Storage(
            name_nice = T("Shelters"),
            #description = "Tracks the location, capacity and breakdown of victims in Shelters",
            restricted = True,
            module_type = 10
        )),
        #("hms", Storage(
        #    name_nice = T("Hospitals"),
        #    #description = "Helps to monitor status of hospitals",
        #    restricted = True,
        #    module_type = 10
        #)),
        ("dvr", Storage(
          name_nice = T("Case Management"),
          #description = "Allow affected individuals & households to register to receive compensation and distributions",
          restricted = True,
          module_type = 10,
        )),
        ("event", Storage(
           name_nice = T("Events"),
           #description = "Activate Events (e.g. from Scenario templates) for allocation of appropriate Resources (Human, Assets & Facilities).",
           restricted = True,
           module_type = 10,
        )),
        ("security", Storage(
           name_nice = T("Security"),
           restricted = True,
           module_type = 10,
        )),
        #("transport", Storage(
        #   name_nice = T("Transport"),
        #   restricted = True,
        #   module_type = 10,
        #)),
        ("stats", Storage(
           name_nice = T("Statistics"),
           #description = "Manages statistics",
           restricted = True,
           module_type = None,
        )),
    ])

# =============================================================================
def drk_default_shelter():
    """
        Lazy getter for the default shelter_id
    """

    s3 = current.response.s3
    shelter_id = s3.drk_default_shelter

    if not shelter_id:
        default_site = current.deployment_settings.get_org_default_site()

        # Get the shelter_id for default site
        if default_site:
            stable = current.s3db.cr_shelter
            query = (stable.site_id == default_site)
            shelter = current.db(query).select(stable.id,
                                            limitby=(0, 1),
                                            ).first()
            if shelter:
                shelter_id = shelter.id

        s3.drk_default_shelter = shelter_id

    return shelter_id

# =============================================================================
def drk_dvr_rheader(r, tabs=[]):
    """ DVR custom resource headers """

    if r.representation != "html":
        # Resource headers only used in interactive views
        return None

    from s3 import s3_rheader_resource, \
                   S3ResourceHeader, \
                   s3_fullname, \
                   s3_yes_no_represent

    tablename, record = s3_rheader_resource(r)
    if tablename != r.tablename:
        resource = current.s3db.resource(tablename, id=record.id)
    else:
        resource = r.resource

    rheader = None
    rheader_fields = []

    if record:
        T = current.T

        if tablename == "pr_person":

            # "Case Archived" hint
            hint = lambda record: SPAN(T("Invalid Case"),
                                       _class="invalid-case",
                                       )

            if current.request.controller == "security":

                # No rheader except archived-hint
                case = resource.select(["dvr_case.archived"], as_rows=True)
                if case and case[0]["dvr_case.archived"]:
                    rheader_fields = [[(None, hint)]]
                    tabs = None
                else:
                    return None

            else:

                if not tabs:
                    tabs = [(T("Basic Details"), None),
                            (T("Family Members"), "group_membership/"),
                            (T("Activities"), "case_activity"),
                            (T("Appointments"), "case_appointment"),
                            (T("Photos"), "image"),
                            (T("Notes"), "case_note"),
                            ]

                case = resource.select(["dvr_case.status_id",
                                        "dvr_case.archived",
                                        "dvr_case.household_size",
                                        "dvr_case.last_seen_on",
                                        "first_name",
                                        "last_name",
                                        "shelter_registration.shelter_unit_id",
                                        ],
                                        represent = True,
                                        raw_data = True,
                                        ).rows

                if case:
                    # Extract case data
                    case = case[0]
                    archived = case["_row"]["dvr_case.archived"]
                    case_status = lambda row: case["dvr_case.status_id"]
                    household_size = lambda row: case["dvr_case.household_size"]
                    last_seen_on = lambda row: case["dvr_case.last_seen_on"]
                    name = lambda row: s3_fullname(row)
                    shelter = lambda row: case["cr_shelter_registration.shelter_unit_id"]
                else:
                    # Target record exists, but doesn't match filters
                    return None

                rheader_fields = [[(T("ID"), "pe_label"),
                                   (T("Case Status"), case_status),
                                   (T("Shelter"), shelter),
                                   ],
                                  [(T("Name"), name),
                                   ],
                                  ["date_of_birth",
                                   (T("Size of Family"), household_size),
                                   (T("Last seen on"), last_seen_on),
                                   ],
                                  ]

                if archived:
                    rheader_fields.insert(0, [(None, hint)])

                # Generate rheader XML
                rheader = S3ResourceHeader(rheader_fields, tabs)(
                                r,
                                table = resource.table,
                                record = record,
                                )

                # Add profile picture
                from gluon import A, URL
                from s3 import s3_avatar_represent
                record_id = record.id
                rheader.insert(0, A(s3_avatar_represent(record_id,
                                                        "pr_person",
                                                        _class = "rheader-avatar",
                                                        ),
                                    _href=URL(f = "person",
                                              args = [record_id, "image"],
                                              vars = r.get_vars,
                                              ),
                                    )
                               )

                return rheader

        elif tablename == "dvr_case":

            if not tabs:
                tabs = [(T("Basic Details"), None),
                        (T("Activities"), "case_activity"),
                        ]

            rheader_fields = [["reference"],
                              ["status_id"],
                              ]

        rheader = S3ResourceHeader(rheader_fields, tabs)(r,
                                                         table=resource.table,
                                                         record=record,
                                                         )

    return rheader

# =============================================================================
def drk_org_rheader(r, tabs=[]):
    """ ORG custom resource headers """

    if r.representation != "html":
        # Resource headers only used in interactive views
        return None

    from s3 import s3_rheader_resource, S3ResourceHeader

    tablename, record = s3_rheader_resource(r)
    if tablename != r.tablename:
        resource = current.s3db.resource(tablename, id=record.id)
    else:
        resource = r.resource

    rheader = None
    rheader_fields = []

    if record:
        T = current.T

        if tablename == "org_facility":

            if not tabs:
                tabs = [(T("Basic Details"), None),
                        ]

            rheader_fields = [["name", "email"],
                              ["organisation_id", "phone1"],
                              ["location_id", "phone2"],
                              ]

        rheader = S3ResourceHeader(rheader_fields, tabs)(r,
                                                         table=resource.table,
                                                         record=record,
                                                         )
    return rheader

# =============================================================================
def drk_cr_rheader(r, tabs=[]):
    """ CR custom resource headers """

    if r.representation != "html":
        # Resource headers only used in interactive views
        return None

    from s3 import s3_rheader_resource, S3ResourceHeader

    tablename, record = s3_rheader_resource(r)
    if tablename != r.tablename:
        resource = current.s3db.resource(tablename, id=record.id)
    else:
        resource = r.resource

    rheader = None
    rheader_fields = []

    if record:
        T = current.T

        if tablename == "cr_shelter":

            if not tabs:
                tabs = [(T("Basic Details"), None),
                        (T("Housing Units"), "shelter_unit"),
                        (T("Client Registration"), "shelter_registration"),
                        ]

            rheader_fields = [["name",
                               ],
                              ["organisation_id",
                               ],
                              ["location_id",
                               ],
                              ]

        rheader = S3ResourceHeader(rheader_fields, tabs)(r,
                                                         table=resource.table,
                                                         record=record,
                                                         )
    return rheader

# END =========================================================================