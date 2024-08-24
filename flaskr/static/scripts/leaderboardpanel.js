const leaderboard_right_panel     = document.getElementById('leaderboard-right-panel');
const leaderboard                 = document.getElementById('leaderboard');
const recommendations             = document.getElementById('rec-content');
const right_panel_title           = document.getElementById('right-title');



var current_right_panel = 'recommendations';

loadLeaderboard();

if(sessionStorage.getItem('current right panel')){
    current_right_panel = sessionStorage.getItem('current right panel');
}

if(current_right_panel == 'recommendations'){
    switchToRecommendations();
}
else if(current_right_panel == 'leaderboard'){
    switchToLeaderboard();
}

leaderboard_right_panel.addEventListener('click', () => {
    if(current_right_panel == 'recommendations'){
        switchToLeaderboard();
        current_right_panel = 'leaderboard';
    }
    else if(current_right_panel == 'leaderboard'){
        switchToRecommendations();
        current_right_panel = 'recommendations';
    }
    updateCurrentPanel();
});

function switchToRecommendations() {
    leaderboard.style.display = 'none';
    recommendations.style.display = 'block';
    right_panel_title.innerHTML = 'Polecane Kanały';
}
function switchToLeaderboard() {
    recommendations.style.display = 'none';
    leaderboard.style.display = 'flex';
    right_panel_title.innerHTML = 'Top 100';
}

function updateCurrentPanel(){
    sessionStorage.setItem('current right panel', current_right_panel);
}


function loadLeaderboard(){
    const leaderboard_url = '/leaderboard';

    fetch(leaderboard_url).then(response => response.json())
        .then(json => {
                var entries = json['entries'];
                for(let i = 0; i < entries; i++){
                    var last = false;
                    if(i + 1 == entries)
                        last = true;
                    createLeaderboardEntry(i + 1, json[i.toString()], last);
                }
            });
}

function createLeaderboardEntry(place, entry, last){
    // Avatar formatting
    var avatar_id;
    if(entry['avatar_id'] == null)
        avatar_id = 'default';
    else
        avatar_id = 'avatar_' + entry['avatar_id'].toString();

    var avatar_url       = '/static/img/avatar/' + avatar_id + '.png';
    var avatar_hover_url = '/static/img/numbers/' + place.toString() + '.png';

    // Points formatting
    var formated_points = formatPoints(entry['points']);

    // Studs choosing
    var stud_url;
    if(place == 1)
        stud_url = '/static/img/stud/purple-lego-stud.gif';
    else if(place == 2)
        stud_url = '/static/img/stud/blue-lego-stud.gif';
    else if(place == 3)
        stud_url = '/static/img/stud/gold-lego-stud.gif';
    else
        stud_url = '/static/img/stud/silver-lego-stud.gif';

    // Creating elements
    var row             = document.createElement("div");
    row.className           = 'container';
    row.id                  = 'lb-row'; 
    setRowStyle(row, last);

    var avatar              = document.createElement("div");
    avatar.id                   = 'lb-avatar';
    setAvatarStyle(avatar);
    var avatar_background       = document.createElement("img");
    avatar_background.id            = 'profile-avatar-background';
    avatar_background.src           = '/static/img/empty.png';
    var avatar_img              = document.createElement("img");
    avatar_img.id                   = 'profile-avatar-img';
    avatar_img.src                  = '/static/img/empty.png';
    setAvatarImagesStyle(avatar_background, avatar_img, avatar_url);

    var username            = document.createElement("div");
    username.className          = 'container';
    username.id                 = 'lb-username';
    var username_text           = document.createElement("span");
    username_text.innerHTML         = entry['username'];
    setUsernameStyle(username, username_text);

    var stud                = document.createElement("div");
    stud.id                     = 'stud';
    var stud_img                = document.createElement("img");
    stud_img.src                    = '/static/img/empty.png';
    setStudStyle(stud, stud_img, stud_url);

    var points              = document.createElement("div");
    points.className            = 'container studs';
    points.id                   = 'lb-points';
    var points_text             = document.createElement("span");
    points_text.innerHTML           = formated_points;
    setPointsStyle(points, points_text);
    
    // Elements assebly
    avatar.appendChild(avatar_background);
    avatar.appendChild(avatar_img);

    username.appendChild(username_text);

    stud.appendChild(stud_img);

    points.appendChild(points_text);

    // Creating events
    avatar.addEventListener('mouseover', () => {
        avatar_img.style.backgroundImage = 'url(' + avatar_hover_url + ')';
    });
    avatar.addEventListener('mouseleave', () => {
        avatar_img.style.backgroundImage = 'url(' + avatar_url + ')';
    });

    username.addEventListener('mouseover', () => {
        if(username_text.scrollWidth > username_text.clientWidth){
            username_text.style.textOverflow = 'clip';
            username_text.style.whiteSpace = 'normal';
            username_text.style.wordBreak = 'break-word';
    
            username_text.style.position = 'fixed';
            username_text.style.right = leaderboard.getBoundingClientRect()['width'].toString() + 'px';
            username_text.style.backgroundColor = '#3a3441bf';
            username_text.style.width = 'auto';
            username_text.style.padding = '1vh';
            username_text.style.fontSize = '2vh';
            username_text.style.border = '2px solid grey';
            username_text.style.zIndex = '2';
            username.style.alignItems = 'center';
        }
    });
    username.addEventListener('mouseleave', () => {
        username_text.style.textOverflow = 'ellipsis';
        username_text.style.overflow = 'hidden';
        username_text.style.whiteSpace = 'nowrap';
        username_text.style.wordBreak = 'initial';
        
        username_text.style.position = 'initial';
        username_text.style.backgroundColor = 'initial';
        username_text.style.width = '90%';
        username_text.style.padding = '0';
        username_text.style.paddingLeft = '5%';
        username_text.style.paddingRight = '5%';
        username_text.style.fontSize = '1.9vh';
        username_text.style.border = '0';
        username_text.style.zIndex = '0';
    });

    // Row assebly
    row.appendChild(avatar);
    row.appendChild(username);
    row.appendChild(stud);
    row.appendChild(points);


    leaderboard.appendChild(row);
}

function formatPoints(points){
    var points_left  = '';
    var points_mid   = Math.round((points % 1000000) / 1000);
    var points_right = (points % 1000);

    if(points > 999999){
        points_left  = Math.round(points / 1000000).toString() + '.';
        points_mid   = format3digit(Math.round((points % 1000000) / 1000).toString()) + '.';
        points_right = format3digit((points % 1000).toString());
    }
    else if(points < 1000000 && points > 999){
        points_left  = '';
        points_mid   = Math.round((points % 1000000) / 1000).toString() + '.';
        points_right = format3digit((points % 1000).toString());
    }
    else{
        points_left  = '';
        points_mid   = '';
        points_right = format3digit((points % 1000).toString());
    }

    var formated_points = points_left + points_mid + points_right;

    return formated_points;
}

function format3digit(points_string){
    if(points_string.length == 2){
        points_string = '0' + points_string;
    }
    else if(points_string.length == 1){
        points_string = '00' + points_string;
    }
    return points_string;
}


function setRowStyle(row, last){
    style = 'height: 4vh; \
            width: calc(100% - 4px); \
            background-color: #707070b2; \
            border: 2px solid var(--col-5); \
            border-bottom: 0; \
            flex-direction: row; \
            justify-content: space-between;';
    if(last)
        style += 'border-bottom: 2px solid var(--col-5);';
    row.style = style;
}
function setAvatarStyle(avatar){
    avatar.style = 'position: relative; \
                    flex-shrink: 0; \
                    width: 4vh; \
                    height: 100%; \
                    border-right: 2px solid var(--col-5);';
}
function setAvatarImagesStyle(avatar_background, avatar_img, avatar_url){
    var style = 'position: absolute; \
                top: 0; \
                left: 0; \
                width: 3.8vh; \
                height: 3.8vh; \
                padding: 0.1vh; \
                border: 0; \
                border-radius: 0; \
                background-size: 3.8vh 3.8vh; \
                background-position: center; \
                background-repeat: no-repeat;';

    avatar_background.style = style + "background-image: url('/static/img/avatar/background_blue_x256.png');";
    avatar_img.style        = style + "background-image: url(\'" + avatar_url + "\');";
}
function setUsernameStyle(username, username_text){
    username.style = 'flex-grow: 0; \
                      flex-shrink: 2; \
                      min-width: 0; \
                      width: 100%; \
                      justify-content: center; ';

    username_text.style = 'flex-grow: 0; \
                           flex-shrink: 2; \
                           width: 90%; \
                           padding-left: 5%; \
                           padding-right: 5%; \
                           font: 1.9vh sans-serif; \
                           color: white; \
                           white-space: nowrap; \
                           overflow: hidden; \
                           text-overflow: ellipsis;';
}
function setPointsStyle(points, points_text){
                    //min-width: 8.7vh; \
    points.style = 'font-size: 2.6vh; \
                    padding-right: 0.5vh; \
                    flex-grow: 0; \
                    flex-shrink: 0; \
                    width: 14.5vh; \
                    text-align: left; \
                    justify-content: center;';
    points_text.style = 'width: auto; \
                        margin: auto; \
                        margin-left: 0;';
}
function setStudStyle(stud, stud_img, stud_url){
    stud.style = 'width: 3.6vh; \
                  flex-shrink: 0; \
                  height: 4vh; \
                  border-left: 2px solid var(--col-5);';

    stud_img.style = 'padding: 0.6vh; \
                      padding-right: 0.2vh; \
                      width: 2.8vh; \
                      height: 2.8vh; \
                      border: 0; \
                      border-radius: 0; \
                      background-size: 2.8vh 2.8vh; \
                      background-position: center; \
                      background-repeat: no-repeat; \
                      background-image: url(\'' + stud_url + '\');';
}