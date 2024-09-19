/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";

import { onMounted, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { ListController } from "@web/views/list/list_controller";

export class ListControllerExtend extends ListController {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.user = useService("user");
    this.action = useService("action");
    this.dialogService = useService("dialog")
    this.menu = useService("menu");
  }

  getCurrentPartnerType() {

    const params = new URLSearchParams(window.location.href); 
    const currentMenuId = params.get("menu_id");  // get menu_id url

    const currentRootMenuItem = this.menu.getCurrentApp(); // get Real Estate root menu -> menu_product_root
    let partnerRootMenuItem = null;
    currentRootMenuItem.childrenTree.forEach(children => {
        if(children.children.includes(parseInt(currentMenuId))) {
          partnerRootMenuItem = children;
        }
    }); // Get partner root menu item
    let currentContactType = "";
    partnerRootMenuItem.childrenTree.forEach(children => {
      if(parseInt(currentMenuId) === children.id) {
        currentContactType = children.name
      }
    });
    
    return {"menu_id": currentMenuId,"menu_name":currentContactType};
  }

  async addPartner() {
    const currentMenu = this.getCurrentPartnerType()["menu_name"];
    let res_model = ""
    // Show different modal to select partner depend on team or friends menu selected
    if(currentMenu === "Bạn bè") {
      res_model="custom.friend.partner";
    } 
    else if(currentMenu === "Đối tác") {
      res_model="custom.partner";
    }
    else if(currentMenu === "Đồng nghiệp") {
      res_model="custom.team";
    }
    const result = await this.orm.call(
      res_model,
      'add_all_partners',
      []
    )
    this.action.doAction({
      type: 'ir.actions.act_window',
      res_model: res_model,
      view_mode: 'tree',
      views: [[false, "tree"]],
      target: "current",
      context: {},
    });
  }
}
ListControllerExtend.template = "real_estate.list_test";

export class ListRendererExtend extends ListRenderer {
  setup() {
    super.setup();
    onMounted(() => {});
    onWillUpdateProps(async (nextProps) => {});
  }
}

registry.category("views").add("list_test", {
  ...listView,
  Controller: ListControllerExtend,
  Renderer: ListRendererExtend,
});
