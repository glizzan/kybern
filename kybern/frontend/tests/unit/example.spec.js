import { shallowMount } from '@vue/test-utils'
import HelloWorld from '@/components/HelloWorld.vue'

import ForumsVuexModule from '@/store/ForumsVuexModule'

describe('HelloWorld.vue', () => {
  it('renders props.msg when passed', () => {
    const msg = 'new message'
    const wrapper = shallowMount(HelloWorld, {
      propsData: { msg }
    })
    expect(wrapper.text()).toMatch(msg)
  })
})


describe('ForumsVuexModule.js', () => {
    it('has no posts', () => {
      expect(ForumsVuexModule.state.posts).toEqual([])
    })
  })