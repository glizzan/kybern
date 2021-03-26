<template>

    <div class="alert" role="alert">

        <div class="row">
            <div class="col-9">
                <p class="font-weight-bold">How does leadership work in Kybern?</p>
            </div>
            <div class="col-3 text-right">
                <span @click="info_visible = !info_visible">
                    <!-- <b-icon-chevron-down v-if="!info_visible"></b-icon-chevron-down> -->
                    <b-button v-if="!info_visible" class="btn-info btn-sm ml-2">Learn more</b-button>
                    <b-icon-chevron-up v-if="info_visible"></b-icon-chevron-up>
                </span>
            </div>
        </div>

        <b-collapse id="more-info" v-model="info_visible">

            <div class="row text-justify" style="font-size: .9rem;">

                <div class="col-12 px-5">

                    <p>Groups can be owned by a combination of individuals and people with specific roles.
                       There must always be at least one person who is an owner.</p>

                    <p>If no conditions are set on the owners' power, this means any one owner can make arbitrary
                       changes to the community, including deleting it. Most communities will not want this, so we
                       recommend setting a condition on your owners. For instance, if you have a large group of owners,
                       you may require that they vote together in order to exercise their power.</p>

                    <p>Often we want to give people power in a community without granting it to them completely or
                       permanently. For instance, if our owners are a large collective of people who take action by
                       voting, we may want to appoint a smaller number of people who can act more quickly and freely.
                       We call these people "governors". Unlike owners, governors are optional.</p>

                    <p>By default, governors can do what they want within the community. However, there are limits.
                       There are certain actions (see below) that only owners can take. Owners may also turn off
                       the governors' "default permissions" for individual resources. Owners may set conditions on
                       governors, for instance, requiring the approval of one owner. And, finally, if they are
                       unhappy with an individual governor or with the governors as a whole, they can remove them.</p>

                    <p class="font-italic">Permissions which require owner approval and cannot be
                        delegated to governors are:</p>

                    <ul>
                        <li>adding and removing owners, both individuals and roles</li>
                        <li>adding and removing governors, both individuals and roles</li>
                        <li>making it so only owners can change a specific resource, or removing that restriction from a
                            specific resource</li> <!-- aka enabling or disabling the foundational permission on an object -->
                        <li>making it so governors cannot change a specific resource, or removing that restriction from a
                            specific resource</li> <!-- aka enabling or disabling the governing permission on an object -->
                    </ul>

                </div>

            </div>

        </b-collapse>

    </div>

</template>

<script type="application/javascript">

export default {

    data: function() {
        return {
            info_visible: false
        }
    }

}

</script>