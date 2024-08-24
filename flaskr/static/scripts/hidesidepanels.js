const left_panel  = document.getElementById('body-left-panel');
const right_panel = document.getElementById('body-right-panel');

const hide_left_panel  = document.getElementById('hide-left-panel');
const hide_right_panel = document.getElementById('hide-right-panel');

// TODO Auto hide panels if width too small
// and prevent to open

var bar_status = 0;
if(parseInt(sessionStorage.getItem('bar status'))){
  bar_status = parseInt(sessionStorage.getItem('bar status'));
}
else{
  bar_status = (bar_status === 0) ? bar_status : 0;
}


function hideLeft() {
    left_panel.style.display = 'none';
    hide_left_panel.style.transform = 'scaleX(-1)'
}
function revealLeft() {
    left_panel.style.display = 'flex';
    hide_left_panel.style.transform = 'scaleX(1)'
}
function hideRight() {
    right_panel.style.display = 'none';
    hide_right_panel.style.transform = 'scaleX(-1)'
}
function revealRight() {
    right_panel.style.display = 'flex';
    hide_right_panel.style.transform = 'scaleX(1)'
}
function updateBarStatus(){
  sessionStorage.setItem('bar status', bar_status);
}

if(bar_status.length == 0){
  revealLeft();
  revealRight();
}
else if(bar_status == 1){
  hideLeft();
}
else if(bar_status == 2){
  hideRight();
}
else if(bar_status == 3){
  hideLeft();
  hideRight();
}


hide_left_panel.addEventListener('click', () => {

  if (left_panel.style.display !== 'none') {
    hideLeft();
    bar_status += 1;
    updateBarStatus();
  }
  else {
    revealLeft();
    bar_status -= 1;
    updateBarStatus();
  }
});

hide_right_panel.addEventListener('click', () => {

  if (right_panel.style.display !== 'none') {
    hideRight();
    bar_status += 2;
    updateBarStatus();
  }
  else {
    revealRight();
    bar_status -= 2;
    updateBarStatus();
  }
});