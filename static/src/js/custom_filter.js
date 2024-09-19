/* @odoo-module */

import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.HelloWorldPopup = publicWidget.Widget.extend({
  selector: "#wrapwrap",

  init() {
    this._super(...arguments);
    this.dialog = this.bindService("dialog");
  },
  start() {
    // this.dialog.add(ConfirmationDialog, {
    //   body: "Hello World",
    //   confirm: () => {
    //     console.log("Confirmation dialog confirmed");
    //   },
    //   cancel: () => {
    //     console.log("Confirmation dialog cancelled");
    //   },
    // });

    // Add event listener for city filter

    const btn_submit = document.getElementById("btn_submit");
    const categoryFilter = document.getElementById("category_filter");
    const cityFilter = document.getElementById("city_filter");
    const directionFilter = document.getElementById("direction_filter");
    const priceFilter = document.getElementById("price_filter");

    if (btn_submit) {
              btn_submit.addEventListener("click", function () {
        let selectedCity = cityFilter.value;
        let selectedCategory = categoryFilter.value;
        let selectedDirection = directionFilter.value;
        let selectedPrice = priceFilter.value;
        const url =
          "/shop?city_filter=" +
          selectedCity +
          "&category_filter=" +
          selectedCategory +
          "&direction_filter=" +
          selectedDirection +
        "&price_filter=" + selectedPrice;
        window.location.href = url;
      });
    }

    //   if (cityFilter) {
    //     cityFilter.addEventListener("change", function () {
    //       let selectedCity = this.value;
    //       window.location.href = "/shop?city_filter=" + selectedCity;
    //     });
    //   }

    //   if (categoryFilter) {
    //     categoryFilter.addEventListener("change", function () {
    //       let selectedCategory = this.value;
    //       window.location.href = "/shop?category_filter=" + selectedCategory;
    //     });
    //   }

    //   if (directionFilter) {
    //     directionFilter.addEventListener("change", function () {
    //       let selectedDirection = this.value;
    //       window.location.href = "/shop?direction_filter=" + selectedDirection;
    //     });
    //   }

    //   $(document).ready(function() {
    //     $('#price_filter').on('change', function() {
    //         this.form.submit();  // Gửi form để áp dụng bộ lọc
    //     });
    // });

    return this._super(...arguments);
  },
});
