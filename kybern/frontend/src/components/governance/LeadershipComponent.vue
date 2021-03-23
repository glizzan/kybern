<template>

    <span>

        <div class="bg-white pt-3 my-3">
            <leadership-guide-alert></leadership-guide-alert>
        </div>

        <div class="bg-white p-3 my-3">
            <p>This group's basic structure is:</p>
            <p class="mt-2 mx-5">{{ governance_info_display }}</p>
        </div>

        <change-leadership-component></change-leadership-component>

    </span>


</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import LeadershipGuideAlert from '../governance/LeadershipGuideAlert'
import ChangeLeadershipComponent from '../governance/ChangeLeadershipComponent'


export default {

    components: { LeadershipGuideAlert, ChangeLeadershipComponent },
    store,
    computed: {
        ...Vuex.mapState({ governance_info: state => state.governance.governance_info }),
        ...Vuex.mapGetters(['getUserName']),
        governance_info_display: function () {
            // This is a hack to replace user ids with username for displaying in leadership

            var current_context = this
            function replace_pk_with_username(string_with_pks_embedded) {
                const digit_regex = /\d+/g
                var new_string = string_with_pks_embedded.replace(digit_regex, function (digit_match) {
                    return current_context.getUserName(digit_match)
                })
                return new_string
            }

            // Replace anything matching "individual N", ending with space, period, or comma
            const single_regex = /individual\s\d+(\s|\.|\s)/g

            // Replace anything matching list of "individuals M and N" or "individuals M, N, O and P",
            // ending with space, period or comma
            // const multiple_regex = /individuals(\s\d+\,)*\s\d+\sand\s\d+(\s|\.|\s)/g  (works but unnecessary escape char)
            const multiple_regex = /individuals(\s\d+,)*\s\d+\sand\s\d+(\s|\.|\s)/g

            var reformatted_string = this.governance_info.replace(single_regex, replace_pk_with_username)
            reformatted_string = reformatted_string.replace(multiple_regex, replace_pk_with_username)
            return reformatted_string
        }
    }

}

</script>
