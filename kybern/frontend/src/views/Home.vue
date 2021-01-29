<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <groupConfigComponent />
  </div>
</template>

<script>
// @ is an alias to /src
//import HelloWorld from '@/components/HelloWorld.vue'
import groupConfigComponent from '@/components/groupConfigComponent.vue'


export default {
  name: 'Home',
  components: {
    groupConfigComponent
  }
}
</script>
