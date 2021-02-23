import Vue from 'vue'
import VueRouter from 'vue-router'
// groups
import GroupConfigComponent from '../components/groups/GroupConfigComponent'
import GroupResourcesComponent from '../components/groups/GroupResourcesComponent'
import EditGroupComponent from '../components/groups/EditGroupComponent'
// actions
import ActionHistoryComponent from '../components/actions/ActionHistoryComponent'
import ActionDetailComponent from '../components/actions/ActionDetailComponent'
// governance
import GovernanceComponent from '../components/governance/GovernanceComponent'
import ChangeLeadershipComponent from '../components/governance/ChangeLeadershipComponent'
import MembershipSettingsComponent from '../components/governance/MembershipSettingsComponent'
// permissions
import ItemPermissionsComponent from '../components/permissions/ItemPermissionsComponent'
import RolePermissionsComponent from '../components/permissions/RolePermissionsComponent'
import PersonPermissionsComponent from '../components/permissions/PersonPermissionsComponent'
import AdvancedPermissionsComponent from '../components/permissions/AdvancedPermissionsComponent'
import ConditionManagerComponent from '../components/conditions/ConditionManagerComponent'
// forums
import ForumFormComponent from '../components/forums/ForumFormComponent'
import ForumListComponent from '../components/forums/ForumListComponent'
import ForumComponent from '../components/forums/ForumComponent'
import PostComponent from '../components/forums/PostComponent'
import PostFormComponent from '../components/forums/PostFormComponent'
// templates
import TemplateComponent from '../components/templates/TemplateComponent'
// lists
import ListFormComponent from '../components/simplelists/ListFormComponent'
import RowFormComponent from '../components/simplelists/RowFormComponent'
import SimpleListComponent from '../components/simplelists/SimpleListComponent'


Vue.use(VueRouter)

const routes = [

    {
        name: 'home',
        path: '/',
        components: {
            sidebar: GroupConfigComponent,
            main: GroupResourcesComponent
        }
    },

    // Group
    {
        name: 'edit-group',
        path: '/edit group',
        meta: { highlight: 'edit-group'},
        components: {
            sidebar: GroupConfigComponent,
            main: GroupResourcesComponent,
            modal: EditGroupComponent
        }
    },

    // Actions
    {
        name: 'action-history',
        path: '/actions/history/:item_id/:item_model/:item_name',
        meta: { highlight: 'history'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ActionHistoryComponent
        }
    },
    {
        name: 'action-detail',
        path: '/actions/detail/:action_id',
        meta: { highlight: 'history'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ActionDetailComponent
        }
    },

    // Templates
    {
        name: 'templates',
        path: '/templates/:scope/',
        meta: { highlight: 'governance'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: TemplateComponent
        }
    },
    {
        name: 'item-templates',
        path: '/templates/:scope/:target_id/:target_model',
        meta: { highlight: 'governance'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: TemplateComponent
        }
    },

    // Governance
    {
        name: 'governance',
        path: '/governance',
        meta: { highlight: 'governance'},
        components: {
            sidebar: GroupConfigComponent,
            main: GovernanceComponent
        }
    },
    {
        name: 'change-leadership',
        path: '/governance/change-leadership',
        meta: { highlight: 'governance'},
        components: {
            sidebar: GroupConfigComponent,
            main: ChangeLeadershipComponent
        }
    },
    {
        name: 'membership-settings',
        path: '/membership-settings',
        meta: { highlight: 'governance'},
        components: {
            sidebar: GroupConfigComponent,
            main: MembershipSettingsComponent
        }
    },


    // Permissions
    {
        name: 'item-permissions',
        path: '/permissions/:item_id/:item_model/:item_name',
        meta: { highlight: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ItemPermissionsComponent
        }
    },
    {
        name: 'role-permissions',
        path: '/permissions/:role_to_edit',
        meta: { highlight: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: RolePermissionsComponent
        }
    },
    {
        name: 'user-permissions',
        path: '/permissions/user/:user_pk',
        meta: { highlight: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: PersonPermissionsComponent
        }
    },
    {
        name: 'advanced-permissions',
        path: '/advanced-permissions/:item_id/:item_model',
        meta: { highlight: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: AdvancedPermissionsComponent
        }
    },
    {
        name: 'conditions',
        path: '/conditions/:conditioned_on/:dependency_scope',
        meta: { highlight: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ConditionManagerComponent
        }
    },

    //Forums
    {
        name: 'add-new-forum',
        path: '/forums/new',
        components: {
            sidebar: GroupConfigComponent,
            main: ForumListComponent,
            modal: ForumFormComponent
        }
    },
    {
        name: 'forum-detail',
        path: '/forums/:forum_id',
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ForumComponent
        }
    },
    {
        name: 'edit-forum',
        path: '/forums/:forum_id/edit',
        props: { sidebar: false, main: true, modal: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ForumComponent,
            modal: ForumFormComponent
        }
    },
    {
        name: 'add-new-post',
        path: '/forums/:forum_id/new_post',
        props: { sidebar: false, main: true, modal: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ForumComponent,
            modal: PostFormComponent
        }
    },
    {
        name: 'edit-post',
        path: '/forums/:forum_id/posts/:post_id/edit',
        props: { sidebar: false, main: true, modal: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ForumComponent,  // switch to postComponent once made
            modal: PostFormComponent
        }
    },
    {
        name: 'post-detail',
        path: '/forums/:forum_id/posts/:post_id',
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: PostComponent
        }
    },

    // Lists
    {
        name: 'add-new-list',
        path: '/lists/new',
        components: {
            sidebar: GroupConfigComponent,
            main: GroupResourcesComponent,
            modal: ListFormComponent
        }
    },
    {
        name: 'edit-list-info',
        path: '/lists/edit/:list_id',
        props: { sidebar: false, main: false, modal: true },
        components: {
            sidebar: GroupConfigComponent,
            main: GroupResourcesComponent,
            modal: ListFormComponent
        }
    },
    {
        name: 'list-detail',
        path: '/lists/detail/:list_id',
        props: { sidebar: false, main: true},
        components: {
            sidebar: GroupConfigComponent,
            main: SimpleListComponent
        }
    },
    {
        name: 'edit-list-row',
        path: '/lists/detail/:list_id/rows/:mode/:row_index',
        props: { sidebar: false, main: true, modal: true},
        components: {
            sidebar: GroupConfigComponent,
            main: SimpleListComponent,
            modal: RowFormComponent
        }
    },
    {
        name: 'add-list-row',
        path: '/lists/detail/:list_id/rows/:mode',
        props: { sidebar: false, main: true, modal: true},
        components: {
            sidebar: GroupConfigComponent,
            main: SimpleListComponent,
            modal: RowFormComponent
        }
    }

]

const router = new VueRouter({
  routes
})

export default router
