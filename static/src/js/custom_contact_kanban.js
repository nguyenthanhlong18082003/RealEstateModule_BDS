/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

import { onMounted, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { KanbanController } from "@web/views/kanban/kanban_controller";

export class KanbanControllerExtend extends KanbanController {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.user = useService("user");
    this.action = useService("action");
    this.dialogService = useService("dialog");
    this.menu = useService("menu");
  }

  getCurrentPartnerType() {
    const params = new URLSearchParams(window.location.href);
    const currentMenuId = params.get("menu_id"); // get menu_id url

    const currentRootMenuItem = this.menu.getCurrentApp(); // get Real Estate root menu -> menu_product_root
    let partnerRootMenuItem = null;
    currentRootMenuItem.childrenTree.forEach((children) => {
      if (children.children.includes(parseInt(currentMenuId))) {
        partnerRootMenuItem = children;
      }
    }); // Get partner root menu item
    let currentContactType = "";
    partnerRootMenuItem.childrenTree.forEach((children) => {
      if (parseInt(currentMenuId) === children.id) {
        currentContactType = children.name;
      }
    });

    return { menu_id: currentMenuId, menu_name: currentContactType };
  }

  async addPartner() {
    const currentMenu = this.getCurrentPartnerType()["menu_name"];
    let res_model = "";
    // Show different modal to select partner depend on team or friends menu selected
    if (currentMenu === "Bạn bè") {
      res_model = "custom.friend.partner";
    } else if (currentMenu === "Đối tác") {
      res_model = "custom.partner";
    } else if (currentMenu === "Đồng nghiệp") {
      res_model = "custom.team";
    }
    const result = await this.orm.call(res_model, "add_all_partners", []);
    this.action.doAction({
      type: "ir.actions.act_window",
      res_model: res_model,
      view_mode: "tree",
      views: [[false, "tree"]],
      target: "current",
      context: {},
    });
  }

  // async onSave(record) { // This function will be called after the form is saved
  //   const currentMenu = this.getCurrentPartnerType()["menu_name"];
  //   let request_type = ""
  //   if(currentMenu["menu_name"] === "Bạn bè") {
  //     request_type = "sent_friend_request";
  //   }
  //   else if(currentMenu["menu_name"] === "Đối tác") {
  //     request_type = "sent_partner_request";
  //   }
  //   else if(currentMenu["menu_name"] === "Đồng nghiệp") {
  //     request_type = "sent_team_request";
  //   }
  //   let partner_id = record.data.sent_request[0];
  //   const currentUser = await this.orm.call(
  //     "res.users",
  //     'search_read',
  //     [
  //       [['id','=',this.user.userId]],
  //       ["partner_id"]
  //     ]
  //   )
  //   console.log("Self:",currentUser[0].partner_id[0]);

  //   const result = await this.orm.create("friend.request", [{
  //     request_partner: currentUser[0].partner_id[0],
  //     request_target: partner_id
  //   }]);
  //   console.log(result)
  //   await this.action.doAction('RealEstateModule_BDS.action_sent_friend_request_menu');
  // }
}
KanbanControllerExtend.template = "real_estate.kanban_test";

export class KanbanRendererExtend extends KanbanRenderer {
  setup() {
    super.setup();
    onMounted(() => {});
    onWillUpdateProps(async (nextProps) => {});
  }
}

registry.category("views").add("kanban_test", {
  ...kanbanView,
  Controller: KanbanControllerExtend,
  Renderer: KanbanRendererExtend,
});
