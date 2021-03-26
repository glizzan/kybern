<template>

  <b-modal :id=modal_id_to_use :title=title hide-footer>

        <add-permission-component :default_selection=default_selection :role_to_edit=role_to_edit
            :item_id=item_id :item_model=item_model></add-permission-component>

  </b-modal>

</template>

<script>

import AddPermissionComponent from '../permissions/AddPermissionComponent'

export default {

    props: ['default_selection', 'role_to_edit', 'item_id', 'item_model', 'modal_id', 'item_name'],
    components: { AddPermissionComponent },
    computed: {
        title() { return "Add permission to " + this.item_name },
        modal_id_to_use() { if (this.modal_id) { return this.modal_id } else { return "add-permission-modal" }}
    }

}

</script>