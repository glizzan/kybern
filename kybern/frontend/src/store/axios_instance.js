import axios from 'axios'

/**
 * Config global for axios/django
 */
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';
axios.defaults.headers = { "headers": { 'Content-Type': "application/json" } }

export default axios