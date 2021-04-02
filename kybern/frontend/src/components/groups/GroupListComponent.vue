<template>

    <b-card-group columns>

        <b-card v-for="group in groups" v-bind:key=group.pk>
            <b-card-text>
                <div class="font-weight-bold mb-2">
                    <a class="text-info" :href="group_detail_url(group.pk)">{{group.name}}</a>
                </div>
                {{group.group_description}}
            </b-card-text>
        </b-card>

    </b-card-group>

</template>

<script>

export default {

    props: ['groups'],
    methods: {
        group_detail_url(pk) {
            return "/groups/" + pk + "/#/"  // note: brittle, need to refactor url_map to handle this somehow
        }
    }

}

</script>