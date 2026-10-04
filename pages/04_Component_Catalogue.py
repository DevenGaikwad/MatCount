"""Searchable component catalogue and administrator maintenance."""

import logging

import streamlit as st

from config.constants import Role
from services import master_data_service
from ui.components import data_table, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor()
LOGGER = logging.getLogger(__name__)
page_header("Component Catalogue", "Search normalized categories and electronic components")

try:
    categories = master_data_service.list_categories()
    category_labels = {category.category_name: category.category_id for category in categories}
    category_filter = st.selectbox("Category", ["All"] + list(category_labels))
    search = st.text_input("Search name, part number or specification")
    components = master_data_service.list_components(
        category_id=category_labels.get(category_filter), search=search or None
    )
    data_table(components)

    if actor.role == Role.ADMINISTRATOR.value:
        tab_category, tab_component, tab_update = st.tabs(
            ["New category", "New component", "Update component"]
        )
        with tab_category:
            with st.form("create_category"):
                category_name = st.text_input("Category name")
                description = st.text_area("Description")
                create_category = st.form_submit_button("Create category")
            if create_category:
                master_data_service.create_category(
                    actor, category_name=category_name, description=description
                )
                st.success("Category created.")
                st.rerun()
        with tab_component:
            if not category_labels:
                st.info("Create at least one component category first.")
            else:
                with st.form("create_component"):
                    category_name = st.selectbox("Category", list(category_labels))
                    component_name = st.text_input("Component name")
                    part_number = st.text_input("Part number (optional)")
                    specification = st.text_area("Specification")
                    unit = st.text_input("Unit of measure", "piece")
                    minimum = st.number_input("Minimum stock level", min_value=0, step=1)
                    manufacturer = st.text_input("Manufacturer details (optional)")
                    create_component = st.form_submit_button(
                        "Create component", type="primary"
                    )
                if create_component:
                    master_data_service.create_component(
                        actor,
                        category_id=category_labels[category_name],
                        component_name=component_name,
                        part_number=part_number or None,
                        specification=specification or None,
                        unit_of_measure=unit,
                        minimum_stock_level=int(minimum),
                        manufacturer_details=manufacturer or None,
                    )
                    st.success("Component created.")
                    st.rerun()
        with tab_update:
            if not components:
                st.info("No component is available for update.")
            else:
                component_map = {
                    f"{item.component_id} — {item.component_name}": item
                    for item in components
                }
                selection = st.selectbox("Select component", list(component_map))
                selected = component_map[selection]
                category_reverse = {value: key for key, value in category_labels.items()}
                with st.form("update_component"):
                    edit_category = st.selectbox(
                        "Category",
                        list(category_labels),
                        index=list(category_labels).index(
                            category_reverse[selected.category_id]
                        ),
                    )
                    edit_name = st.text_input("Component name", selected.component_name)
                    edit_part = st.text_input("Part number", selected.part_number or "")
                    edit_spec = st.text_area("Specification", selected.specification or "")
                    edit_unit = st.text_input("Unit of measure", selected.unit_of_measure)
                    edit_minimum = st.number_input(
                        "Minimum stock level",
                        min_value=0,
                        value=int(selected.minimum_stock_level),
                        step=1,
                    )
                    edit_manufacturer = st.text_input(
                        "Manufacturer details", selected.manufacturer_details or ""
                    )
                    update = st.form_submit_button("Save changes")
                if update:
                    master_data_service.update_component(
                        actor,
                        selected.component_id,
                        category_id=category_labels[edit_category],
                        component_name=edit_name,
                        part_number=edit_part or None,
                        specification=edit_spec or None,
                        unit_of_measure=edit_unit,
                        minimum_stock_level=int(edit_minimum),
                        manufacturer_details=edit_manufacturer or None,
                    )
                    st.success("Component updated.")
                    st.rerun()
except Exception as exc:
    LOGGER.exception("Component catalogue operation failed")
    show_error(exc)
