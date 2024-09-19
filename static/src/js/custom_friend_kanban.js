/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

import { Dialog } from "@web/core/dialog/dialog";

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

  async onClickTest() {
    let form_view_ref = "";
    const params = new URLSearchParams(window.location.href);
    const currentMenuId = params.get("menu_id"); // get menu_id url

    const currentRootMenuItem = this.menu.getCurrentApp(); // get Real Estate root menu -> menu_product_root
    let partnerRootMenuItem = null;
    currentRootMenuItem.childrenTree.forEach((children) => {
      if (children.name === "Partner") {
        partnerRootMenuItem = children;
      }
    }); // Get partner root menu item
    let currentContactType = "";
    partnerRootMenuItem.childrenTree.forEach((children) => {
      if (parseInt(currentMenuId) === children.id)
        currentContactType = children.name;
    });

    console.log(currentContactType);

    // Show different modal to select partner depend on team or friends menu selected
    if (currentContactType === "Bạn bè") {
      form_view_ref = "RealEstateModule_BDS.view_partner_form_with_friend";
    } else if (currentContactType === "Đối tác") {
      form_view_ref = "RealEstateModule_BDS.view_partner_form_with_co_partner";
    } else if (currentContactType === "Đồng nghiệp") {
      form_view_ref = "RealEstateModule_BDS.view_partner_form_with_team";
    }

    // Get current user
    const currentUser = await this.orm.call("res.users", "search_read", [
      [["id", "=", this.user.userId]], // condition
      ["partner_id"], // what u want to get
    ]);

    if (currentUser.length > 0) {
      const currentPartnerId = currentUser[0].partner_id[0];
      this.action.doAction({
        type: "ir.actions.act_window",
        res_model: "res.partner",
        views: [[false, "form"]],
        target: "new",
        res_id: currentPartnerId,
        context: {
          form_view_ref: form_view_ref,
        },
      });
    }
  }
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
