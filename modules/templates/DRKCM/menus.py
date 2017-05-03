# -*- coding: utf-8 -*-

from gluon import current
from s3 import *
from s3layouts import *
try:
    from .layouts import *
except ImportError:
    pass
import s3menus as default

# =============================================================================
class S3MainMenu(default.S3MainMenu):
    """ Custom Application Main Menu """

    # -------------------------------------------------------------------------
    @classmethod
    def menu(cls):
        """ Compose Menu """

        # Modules menus
        main_menu = MM()(
            cls.menu_modules(),
        )

        # Additional menus
        current.menu.personal = cls.menu_personal()
        current.menu.lang = cls.menu_lang()
        current.menu.about = cls.menu_about()
        current.menu.org = cls.menu_org()

        return main_menu

    # -------------------------------------------------------------------------
    @classmethod
    def menu_modules(cls):
        """ Custom Modules Menu """

        from config import drk_default_shelter
        shelter_id = drk_default_shelter()

        has_role = current.auth.s3_has_role
        not_admin = not has_role("ADMIN")

        if not_admin and has_role("SECURITY"):
            return [
                MM("Cases", c="security", f="person"),
                #MM("ToDo", c="project", f="task"),
                MM("Confiscation", c="security", f="seized_item"),
            ]

        elif not_admin and has_role("QUARTIER"):
            return [
                MM("Cases", c=("dvr", "cr"), f=("person", "shelter_registration")),
                MM("Confiscation", c="security", f="seized_item"),
            ]

        else:
            return [
                MM("Cases", c=("dvr", "pr")),
                MM("Event Registration", c="dvr", f="case_event",
                   m = "register",
                   p = "create",
                   # Show only if not authorized to see "Cases"
                   check = lambda this: not this.preceding()[-1].check_permission(),
                   ),
                MM("ToDo", c="project", f="task"),
                MM("Housing Units", c="cr", f="shelter",
                   t = "cr_shelter_unit",
                   args = [shelter_id, "shelter_unit"],
                   check = shelter_id is not None,
                   ),
                homepage("vol"),
                homepage("hrm"),
                MM("More", link=False)(
                    MM("Facilities", c="org", f="facility"),
                    #homepage("req"),
                    homepage("inv"),
                    ),
            ]

    # -------------------------------------------------------------------------
    @classmethod
    def menu_org(cls):
        """ Custom Organisation Menu """

        OM = S3OrgMenuLayout
        return OM()

    # -------------------------------------------------------------------------
    @classmethod
    def menu_lang(cls):

        s3 = current.response.s3

        # Language selector
        menu_lang = ML("Language", right=True)
        for language in s3.l10n_languages.items():
            code, name = language
            menu_lang(
                ML(name, translate=False, lang_code=code, lang_name=name)
            )
        return menu_lang

    # -------------------------------------------------------------------------
    @classmethod
    def menu_personal(cls):
        """ Custom Personal Menu """

        auth = current.auth
        s3 = current.response.s3
        settings = current.deployment_settings

        ADMIN = current.auth.get_system_roles().ADMIN

        if not auth.is_logged_in():
            request = current.request
            login_next = URL(args=request.args, vars=request.vars)
            if request.controller == "default" and \
               request.function == "user" and \
               "_next" in request.get_vars:
                login_next = request.get_vars["_next"]

            self_registration = settings.get_security_self_registration()
            menu_personal = MP()(
                        MP("Register", c="default", f="user",
                           m = "register",
                           check = self_registration,
                           ),
                        MP("Login", c="default", f="user",
                           m = "login",
                           vars = {"_next": login_next},
                           ),
                        MP("Lost Password", c="default", f="user",
                           m = "retrieve_password",
                           ),
                        )
        else:
            s3_has_role = auth.s3_has_role
            is_org_admin = lambda i: not s3_has_role(ADMIN) and \
                                     s3_has_role("ORG_ADMIN")
            menu_personal = MP()(
                        MP("Administration", c="admin", f="index",
                           restrict = ADMIN,
                           ),
                        MP("Administration", c="admin", f="user",
                           check = is_org_admin,
                           ),
                        MP("Profile", c="default", f="person"),
                        MP("Change Password", c="default", f="user",
                           m = "change_password",
                           ),
                        MP("Logout", c="default", f="user",
                           m = "logout",
                           ),
            )
        return menu_personal

    # -------------------------------------------------------------------------
    @classmethod
    def menu_about(cls):

        ADMIN = current.auth.get_system_roles().ADMIN

        menu_about = MA(c="default")(
            MA("Help", f="help"),
            #MA("Contact", f="contact"),
            MA("Version", f="about", restrict = ADMIN),
        )
        return menu_about

# =============================================================================
class S3OptionsMenu(default.S3OptionsMenu):
    """ Custom Controller Menus """

    # -------------------------------------------------------------------------
    @staticmethod
    def cr():
        """ CR / Shelter Registry """

        from config import drk_default_shelter
        shelter_id = drk_default_shelter()

        if not shelter_id:
            return None

        ADMIN = current.auth.get_system_roles().ADMIN

        return M(c="cr")(
                    M("Shelter", f="shelter", args=[shelter_id])(
                        M("Housing Units",
                          t = "cr_shelter_unit",
                          args = [shelter_id, "shelter_unit"],
                          ),
                    ),
                    #M("Room Inspection", f = "shelter", link=False)(
                    #      M("Register",
                    #        args = [shelter_id, "inspection"],
                    #        t = "cr_shelter_inspection",
                    #        p = "create",
                    #        ),
                    #      M("Overview", f = "shelter_inspection"),
                    #      M("Defects", f = "shelter_inspection_flag"),
                    #      ),
                    #M("Administration",
                    #  link = False,
                    #  restrict = (ADMIN, "ADMIN_HEAD"),
                    #  selectable=False,
                    #  )(
                    #    M("Shelter Flags", f="shelter_flag"),
                    #    ),
                )

    # -------------------------------------------------------------------------
    @staticmethod
    def dvr():
        """ DVR / Disaster Victim Registry """

        due_followups = current.s3db.dvr_due_followups() or "0"
        follow_up_label = "%s (%s)" % (current.T("Due Follow-ups"),
                                       due_followups,
                                       )

        ADMIN = current.auth.get_system_roles().ADMIN

        return M(c="dvr")(
                    M("Current Cases", c=("dvr", "pr"), f="person",
                      vars = {"closed": "0"})(
                        M("Create", m="create", t="pr_person", p="create"),
                        M("All Cases", vars = {}),
                        ),
                    M("Activities", f="case_activity")(
                        M("Emergencies",
                          vars = {"~.emergency": "True"},
                          ),
                        M(follow_up_label, f="due_followups"),
                        M("All Activities"),
                        M("Report", m="report"),
                        ),
                    M("Appointments", f="case_appointment")(
                        M("Overview"),
                        M("Import Updates", m="import", p="create",
                          restrict = (ADMIN, "ADMINISTRATION", "ADMIN_HEAD"),
                          ),
                        M("Bulk Status Update", m="manage", p="update",
                          restrict = (ADMIN, "ADMINISTRATION", "ADMIN_HEAD"),
                          ),
                        ),
                    M("Archive", link=False)(
                        M("Closed Cases", f="person",
                          vars={"closed": "1"},
                          ),
                        M("Invalid Cases", f="person",
                          restrict = (ADMIN, "ADMINISTRATION", "ADMIN_HEAD"),
                          vars={"archived": "1"},
                          ),
                        ),
                    M("Administration", restrict=(ADMIN, "ADMIN_HEAD"))(
                        M("Flags", f="case_flag"),
                        M("Case Status", f="case_status"),
                        M("Appointment Types", f="case_appointment_type"),
                        ),
                    )

    # -------------------------------------------------------------------------
    @staticmethod
    def org():
        """ ORG / Organization Registry """

        ADMIN = current.session.s3.system_roles.ADMIN

        return M(c="org")(
                    #M("Organizations", f="organisation")(
                        #M("Create", m="create"),
                        #M("Import", m="import")
                    #),
                    M("Facilities", f="facility")(
                        M("Create", m="create"),
                    ),
                    #M("Organization Types", f="organisation_type",
                      #restrict=[ADMIN])(
                        #M("Create", m="create"),
                    #),
                    M("Facility Types", f="facility_type",
                      restrict=[ADMIN])(
                        M("Create", m="create"),
                    ),
                 )

    # -------------------------------------------------------------------------
    @staticmethod
    def project():
        """ PROJECT / Project/Task Management """

        return M(c="project")(
                 M("Tasks", f="task")(
                    M("Create", m="create"),
                    M("My Open Tasks", vars={"mine":1}),
                 ),
                )

    # -------------------------------------------------------------------------
    @staticmethod
    def security():
        """ SECURITY / Security Management """

        return M(c="security")(
                M("Confiscation", f="seized_item")(
                    M("Create", m="create"),
                    M("Item Types", f="seized_item_type"),
                    ),
                )

# END =========================================================================