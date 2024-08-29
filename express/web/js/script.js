//Page Transition
title_and_des = {
    "Terminal": ["Terminal", "슈비서의 명령어를 직접 입력할 수 있습니다."],
    "Constants": ["Constants", "슈비서의 상수들을 직접 변경할 수 있습니다."],
    "Tokens": ["Tokens", "슈비서의 토큰 값들을 관리할 수 있습니다. 보안이 필요한 페이지입니다."],
    "GPT": ["GPT Settings", "GPT 관련 설정을 할 수 있습니다."],
    "Logout": ["Log Out", "로그아웃 합니다."],
    "Account": ["Account", "슈비서 관리자 계정을 관리할 수 있습니다."]
};

menuItems = document.querySelectorAll('header ul > article');
contents = document.querySelectorAll('.content > div');

title = document.querySelector('.title h1');
des = document.querySelector('.description h2');

menuItems.forEach(function(item) {
    item.addEventListener("click", function(event){
        menuItems.forEach(function(el) {
            // contents[idx].classList.remove('on');
            el.classList.remove('on');
            
            // if(el == item) {
            //     selected = idx;
            // }

        });

        contents.forEach(function(el) {
            el.classList.remove('on');
            if(el.classList[0] == item.classList[0]){
                el.classList.add('on');
            }
        })
        
        item.classList.add('on');
        // contents[selected].classList.add('on');

        title.textContent = title_and_des[item.classList[0]][0];
        des.textContent = title_and_des[item.classList[0]][1];
    }) 
}
);


//Terminal

async function handleCommand(input) {
    response = await fetch('/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: input }),
    })
    .then(response => {
        console.log("response recieved!");
        return response.json();
    })
    .then(data => {
        if(data.status == 200) {
            console.log(data.response);
            output = data.response.replaceAll("\n", "<br />");
            return output;
        }
        else {
            return null;
        }
    }
    );

    return response;
}

document.getElementById('input').addEventListener('keydown', async function(event) {
    if (event.key == 'Enter') {
        event.preventDefault();
        const inputElement = event.target;
        const inputValue = inputElement.value.trim();
        const prompt = document.querySelector('.prompt');

        if (inputValue) {
            const outputElement = document.getElementById('output');
            const command = document.createElement('div');
            command.textContent = `> ${inputValue}`;
            outputElement.appendChild(command);
            
            // 입력 필드 초기화
            inputElement.value = '';
            prompt.textContent = '';

            // 명령어에 대한 답변
            const response = document.createElement('div');
            response.innerHTML = await handleCommand(inputValue);
            outputElement.appendChild(response);

            // 스크롤을 맨 아래로
            outputElement.scrollTop = outputElement.scrollHeight;
            
            prompt.textContent = '> ';
        }
    }
})


document.querySelector('main .Terminal > i').addEventListener('click', function(event) {
    const outputElement = document.getElementById('output');
    while(outputElement.hasChildNodes){
        outputElement.removeChild(outputElement.firstChild);
    }
})

//Constants


//Tokens

//GPT
const textarea = document.querySelector('.GPT textarea');

textarea.addEventListener('input', function(){
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});

//Account
