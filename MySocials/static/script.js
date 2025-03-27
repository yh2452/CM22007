function tristateHandler(checkbox) {
    const states = ['true', 'null', 'false']
  
    const i = states.indexOf(checkbox.target.value) + 1
    checkbox.target.value = i < states.length ? states[i] : states[0]
    switch(checkbox.target.value) {
      case states[0]:
        checkbox.target.checked = true
        console.log("Checked")
        break
      case states[1]:
        checkbox.target.indeterminate = true
        console.log("Indeterminate")
        break
      default:
        checkbox.target.checked = false
        console.log("Unchecked")    
    }
  }
  
  document.querySelector('input[type=checkbox]').onclick = tristateHandler