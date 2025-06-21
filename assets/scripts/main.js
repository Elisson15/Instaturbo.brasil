
import { Menu } from "./menu.js"


const productsCards = document.querySelectorAll('.product')


// action menu

Menu.buttonMenu.onclick = ()=>{
    Menu.open()
    productsCards.forEach((produto)=>{
        produto.addEventListener('mouseover', ()=>{
        })
    })
}

productsCards.forEach(function(product){
    product.addEventListener('mouseover', ()=>{
    if(Menu.menuLinks.classList.contains('visible')){
        Menu.open()
        product.removeEventListener('mouseover', ()=>{})
        }
    })
})


document.addEventListener('click', (event)=>{
    if(event.target !== Menu.menuLinks && event.target !== Menu.buttonMenu){
        Menu.close()
    }
})







