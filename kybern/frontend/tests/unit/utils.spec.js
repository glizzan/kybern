import { mount, shallowMount } from '@vue/test-utils'

import ErrorComponent from '@/components/utils/ErrorComponent.vue'
import { UtilityMixin, ConfiguredFieldsMixin } from '@/components/utils/Mixins'

import { swap_aliases } from '../../src/utilities/utils'


const factory = (values = {}) => {
    return shallowMount(ErrorComponent, {
      data () {
        return {
          ...values
        }
      }
    })
  }

const factory2 = (values = {}) => {
    return shallowMount(ErrorComponent, {
        propsData: {
            ...values
        }
    })
}


describe('ErrorComponent.vue', () => {
    it('default values of error component"', () => {
      expect(ErrorComponent.data().styleclass).toEqual("text-danger")
      expect(ErrorComponent.data().unique_identifier).toEqual(null)
      expect(ErrorComponent.data().show_dismissible_alert).toEqual(true)
    })
    it('renders template', () => {
        const wrapper = factory2({message: "There was an error"})
        expect(wrapper.props().message).toBe("There was an error")
        expect(wrapper.find('.text-danger').text()).toEqual('There was an error')
    })

    // Ignore for now - need to figure how how to handle sub-components, esp from third party libraries
    // it('shows alert when dismissable is true', () => {
    //     const wrapper = factory2({message: "There was an error", dismissable: true})
    //     expect(wrapper.find('.error-alert').text()).toEqual('There was an error')
    // })

  })

describe('UtilityMixin', () => {
    it('shortens text', () => {
        var text = "This is some text. It's definitely some text! Wow, so much text. Impressive how much text there is."
        expect(UtilityMixin.methods.shorten_text(text)).toEqual("This is some text. It's definitely some text! Wow,...")
        expect(UtilityMixin.methods.shorten_text(text, 10)).toEqual("This is so...")
    })
})

describe('swap_aliases', () => {
    it('swaps aliases', () => {
        var alias_dict = {hi: "alias_hi", bye: "alias_bye"}
        var user_permissions = {hi: true, woah: true, yo: false, bye: true}
        var combined = {alias_hi: true, woah: true, yo: false, alias_bye: true}
        expect(swap_aliases(alias_dict, user_permissions)).toEqual(combined)
    })
})