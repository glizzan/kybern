<template>

    <div id="navbarVueApp">
        <b-navbar toggleable="lg" type="dark" variant="info">
            <!-- Left aligned nav items -->
            <b-navbar-brand href="/">Kybern</b-navbar-brand>
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
            <b-collapse id="nav-collapse" is-nav>
            <b-navbar-nav>
            <b-nav-item href="/?hide_info=true">Groups</b-nav-item>
            </b-navbar-nav>
            <!-- Right aligned nav items -->
            <b-navbar-nav class="ml-auto">

                <!-- If user is logged in -->
                <b-nav-item-dropdown right v-if="signed_in">
                    <!-- Using 'button-content' slot -->
                    <template v-slot:button-content><em>{{ user_name }}</em></template>
                    <b-dropdown-item href="/profile">Your Profile</b-dropdown-item>
                    <b-dropdown-item href="/logout">Sign Out</b-dropdown-item>
                </b-nav-item-dropdown>

                <!-- If not logged in, show login page. -->
                <b-nav-item v-else href="/login" >Sign In</b-nav-item>

            </b-navbar-nav>
            </b-collapse>
        </b-navbar>
    </div>

</template>


<script>

export default {

    props: ["user_name", "signed_in"]

}

</script>
