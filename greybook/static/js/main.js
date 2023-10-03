dayjs.extend(window.dayjs_plugin_relativeTime)
dayjs.extend(window.dayjs_plugin_utc)
dayjs.extend(window.dayjs_plugin_localizedFormat)

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

function renderAllDatetime() {
  // render normal time
  const elements = document.querySelectorAll('.dayjs')
  elements.forEach(elem => {
    const date = dayjs.utc(elem.innerHTML)
    const format = elem.dataset.format ?? 'LL'
    elem.innerHTML = date.local().format(format)
  })
  // render from now time
  const fromNowElements = document.querySelectorAll('.dayjs-from-now')
  fromNowElements.forEach(elem => {
    const date = dayjs.utc(elem.innerHTML)
    elem.innerHTML = date.local().fromNow()
  })
  // render tooltip time
  const toolTipElements = document.querySelectorAll('.dayjs-tooltip')
  toolTipElements.forEach(elem => {
    const date = dayjs.utc(elem.dataset.timestamp)
    const format = elem.dataset.format ?? 'LLL'
    elem.dataset.bsTitle = date.local().format(format)
    const tooltip = new bootstrap.Tooltip(elem)
  })
}

document.addEventListener('DOMContentLoaded', renderAllDatetime)
