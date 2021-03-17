<template>

    <b-modal :id=modal_id_to_use :title=title size="xl">

        <p v-if="!permissions.length" class="mt-3">No permissions have been set yet.</p>

        <edit-permission-component v-for="permission in permissions" v-bind:key="permission.pk"
            :permission=permission :item_id=item_id :item_model=item_model class="mt-3">
        </edit-permission-component>

    </b-modal>

</template>

<script>

import EditPermissionComponent from '../permissions/EditPermissionComponent'


export default {

    props: ['permissions', 'item_id', 'item_model', 'item_name', 'modal_id'],
    components: {  EditPermissionComponent },
    computed: {
        title() { return "Edit permissions for " + this.item_name },
        modal_id_to_use() { if (this.modal_id) { return this.modal_id } else { return "edit-permissions-modal" }}
    }
}

</script>