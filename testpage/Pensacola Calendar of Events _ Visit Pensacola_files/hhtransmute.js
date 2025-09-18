(function(){function g(a){return(a=document.cookie.match(new RegExp("(?:^|; )"+a.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g,"\\$1")+"=([^;]*)")))?decodeURIComponent(a[1]):void 0}function w(a){"undefined"==typeof a&&(a=0);a++;a<=p&&(document.cookie="r="+a+"; path=/; expires="+(new Date((new Date).getTime()+1E3*parseInt("7200",10))).toUTCString())}function l(a,c){if("s"!=c&&"s"==b.src||!b.src||b.acc>a.coords.accuracy){b.lat=a.coords.latitude;b.lon=a.coords.longitude;b.acc=a.coords.accuracy;b.src=
c;a=b.lon;var e=b.acc,d=b.src,h=new Date((new Date).getTime()+864E5);document.cookie="lat="+b.lat+"; path=/; expires="+h.toUTCString();document.cookie="lon="+a+"; path=/; expires="+h.toUTCString();document.cookie="acc="+e+"; path=/; expires="+h.toUTCString();document.cookie="src="+d+"; path=/; expires="+h.toUTCString();f&&f.lat==b.lat&&f.lon==b.lon||m("hit",c)}}function x(){var a=g("r");g("acs");w(a);(!a||a<p)&&navigator.geolocation&&navigator.geolocation.getCurrentPosition(function(c){document.cookie=
"acs=1; path=/; expires="+(new Date((new Date).getTime()+1E3*parseInt("7200",10))).toUTCString();l(c,"s");navigator.geolocation.getCurrentPosition(function(e){l(e,"g")},function(){},{maximumAge:12E5,timeout:6E5,enableHighAccuracy:!0});navigator.geolocation.watchPosition(function(e){l(e,"t")},function(){},{maximumAge:12E5,timeout:6E5,enableHighAccuracy:!0})})}function q(a){var c=g("fullthrottlelims_t2");"undefined"!=typeof c&&c!=k&&(r=k,k=c);document.cookie="fullthrottlelims_t2="+k+"; path=/; expires="+
(new Date((new Date).getTime()+63072E7)).toUTCString();a?(n=!0,t()):u=!0;c=g("lat");var e=g("lon"),d=g("acc"),h=g("src");b={};if(c||e)b.lat=c,b.lon=e,b.acc=d;d||(b.acc=0);b.src=h?h:"";if(!a||a&&!u)x(),m("hit","");"undefined"!=typeof fullthrottlelims_cookie_init&&fullthrottlelims_cookie_init(a)}function v(){var a=n?"fullthrottlelims_pxl_image":"fullthrottlelims_pxl_image_t",c=document.createElement("img");c.id=a;c.style.cssText="display: none;";document.body.appendChild(c);return a}function t(){var a=
document.getElementById("fullthrottlelims_pxl_image");if(a){var c=document.getElementById("fullthrottlelims_pxl_image_t");c&&c.remove()}else if(a=document.getElementById("fullthrottlelims_pxl_image_t"),a)n&&(a.remove(),a=v(),a=document.getElementById(a));else if(document.body)a=v(),a=document.getElementById(a);else return null;return a}function m(a,c){var e=t();if(e){var d="https://hits3.livemarketshoppers.com/fullthrottlelims_pxl.gif?c="+k+"&r="+((new Date).getTime()+"-"+Math.random())+"&f="+escape(document.referrer)+"&b="+
escape(navigator.userAgent)+"&l="+escape(navigator.language||navigator.g)+"&p="+escape(window.location.href)+"&o="+r;b&&"undefined"!=typeof b.lat&&(d+="&t="+b.lat,d+="&n="+b.lon,d+="&acc="+b.acc,d+="&src="+b.src,f={},f.lat=b.lat,f.lon=b.lon,f.acc=b.acc,f.src=b.src);d=d+("&s=6490&hs="+c+"&ss=1&ly=1&z=")+(new Date).getTimezoneOffset();e.src=d}else setTimeout(function(){m(a,c)},100)}var k="4310816599",b,f,p=parseInt("1",10),n=!1,u=!1,r="";document.addEventListener("DOMContentLoaded",
function(){q(1)});q(0)})();
 (function() {


let fullthrottlelims_actions_client_id = 6490;
let fullthrottlelims_actions_client_type = 1;
let fullthrottlelims_actions_form_type = 'inline';
let fullthrottlelims_actions_customer_id = "4310816599";
let fullthrottlelims_actions_iframe_num = 1;
let fullthrottlelims_actions_iframes_data = Array();
let fullthrottlelims_actions_register_url = 'https://hits3.livemarketshoppers.com/'+'native-forms.php';
let fullthrottlelims_actions_storageName = "Native-POC-Cat";


function setup_forms_event(doc='',iframe_id='')
{
    if( ! doc )
    {
        doc = document;
    }

    let forms = doc.querySelectorAll('form');

    forms.forEach((form) => {
       let form_id = form.getAttribute('data-ft-form-id');
       if( ! form_id && can_we_set_onsubmit_handler_for_the_form(form))
       {
           form.setAttribute('data-ft-form-id', generate_form_id( form ) );

           form.addEventListener('submit',  function (event) {
             record_submit_data(event );
           }, true);  
       }

    });

    fullthrottlelims_actions_form_type = 'ajax'; //next run , now all dom processed
}

function generate_form_id( form )
{
    const serializer = new XMLSerializer();
    let serializedString = serializer.serializeToString(form);
    let form_id = '';

    //console.log( serializedString );
    form_id += sha256(serializedString);

    return form_id;
}

function setup_input_events(doc='',iframe_id='')
{
    if( ! doc )
    {
        doc = document;
    }
return;
    let selectors = Array( 'input.change', 'select.change', 'textarea.change', 'button.click' );

    selectors.forEach(function(selector_event)
    {
           let option = selector_event.split('.');
           let selector = option[0];
           let event_type = option[1];
           let text_inputs = doc.querySelectorAll(selector);  //textarea , select as well

           text_inputs.forEach((text_input) => {
               let element_event = text_input.getAttribute('data-ft-elem-event');
               if( ! element_event ) 
               {
//console.log( "found" , text_input );
                   text_input.setAttribute('data-ft-elem-event', 1);
                   text_input.addEventListener(event_type, function (event) 
                   {
                           record_data(event_type, event.target , null, event.type);
                   }, true);
               }
           });
    });

}

function build_iframe_data( iframe )
{

    return null;
}

function setup_iframe_events()
{
   let iframes = document.querySelectorAll('iframe');
   iframes.forEach((iframe) => 
   {
        try
          {
             let iframe_id = fullthrottlelims_actions_iframe_num;
             if( ! iframe.getAttribute('data-ft-iframe-num') )
             {
                 fullthrottlelims_actions_iframes_data[fullthrottlelims_actions_iframe_num] = build_iframe_data(iframe);
                 iframe.setAttribute('data-ft-iframe-num', fullthrottlelims_actions_iframe_num);
                 fullthrottlelims_actions_iframe_num++;
             }
             else
             {
                 iframe_id = iframe.getAttribute('data-ft-iframe-num');
             }

             let iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
             setup_forms_event(iframeDocument, iframe_id);
             setup_input_events(iframeDocument, iframe_id);


          } catch(e) {
            //console.log(e);
         }

   });
}

function fullthrottlelims_pxl_getCookie(name) {
  var matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}



function do_it()
{

//console.log( fullthrottlelims_pxl_getCookie('t2') );
//console.log( fullthrottlelims_pxl_getCookie('fullthrottlelims_t2') );

    submit_recorded_data();
    setup_forms_event();
    setup_input_events();
    setup_iframe_events();

    setTimeout(do_it, 1000);
}


function get_form_info(element, element_type)
{
   let form;
   if( element_type == 'form' )
   {
       form = element;
   }
   else
   {
      form = element.form;
   }

   let form_info = {};
   if( ! form )
   {
       return null;
   }

   let form_attributes = form.attributes;
   for (let i = 0; i < form_attributes.length; i++) {
     let attribute = form_attributes[i];
     form_info[attribute.name] = attribute.value;
   }


/*
   form_info.id = form.getAttribute('id');
   form_info.name = form.name;
   form_info.action = form.action;
   form_info.internal_id = form.getAttribute('data-ft-form-id');
*/

   form_info.input = Array();

   Array.from(form.elements).forEach((input) => {
     form_info.input.push(
             {
               name: input.name, 
               value: get_field_value(input)
             } );
   });

   return form_info;
}


function get_recording_data(event, element , element_type = '', event_type = '')
{
try {
        //whole form information
        form_info = get_form_info(element, element_type);

        result = {};
        if( element_type != 'form' )
        {
              //trigger element info
              let element_info = {};

              element_info.name = element.name;
              element_info.id = element.id;
              element_info.txt = '';

              if( element.nodeName == 'BUTTON' )
              {
                 element_info.txt = element.innerHTML;
              }
              element_info.val = get_field_value(element);
              result.elm = element_info;
        }
       
        //final result 
        result.form = form_info;
        result.action = event_type;
        result.customerid = get_customer_id();
        result.clientid = fullthrottlelims_actions_client_id;
        result.client_type = fullthrottlelims_actions_client_type;

        result.page = escape(window.location.href);
        result.browser = escape(navigator.userAgent);
        result.timestamp = new Date().getTime();

 } catch (error) 
   {
       //console.error('Problem:', error);
    }


        return result;
}


function get_customer_id()
{
    if( typeof( window.fullthrottle_customerid ) != 'undefined' )
    {
        return window.fullthrottle_customerid;
    }

    return fullthrottlelims_actions_customer_id;
}

function record_submit_data( event )
{
    let submitting_data = get_recording_data('submit', event.target , 'form', event.type );
    sessionStorage.setItem(fullthrottlelims_actions_storageName, JSON.stringify( submitting_data ) );
}

function submit_recorded_data()
{
   let submitting_data = sessionStorage.getItem( fullthrottlelims_actions_storageName );
   if( submitting_data === null )
   {
       return;
   }
   sessionStorage.removeItem(fullthrottlelims_actions_storageName);

   try {
           const response = fetch(fullthrottlelims_actions_register_url,  { 
             method: 'POST', 
             headers: { 
               'Content-Type': 'application/json', 
             }, 

             body: submitting_data,
           }); 


    } catch (error) 
      {
          //console.error('There was a problem with your fetch operation:', error);
       }


}


async function record_data_fetch(event_main_type, element , element_type = '', event_type = '')
{

let submitting_data = get_recording_data(event_main_type, element , element_type, event_type );

try {
        const response = await fetch(fullthrottlelims_actions_register_url,  { 
          method: 'POST', 
          headers: { 
            'Content-Type': 'application/json', 
          }, 

          body: JSON.stringify(submitting_data),
        }); 

       if (!response.ok) {
           throw new Error('Network response was not ok ' + response.statusText);
       }

        const result = await response.text();

 } catch (error) 
   {
       //console.error('There was a problem with your fetch operation:', error);
    }

}


async function record_data(event_main_type, element , element_type = '', event_type = '', event='', callback_function = '')
{

let submitting_data = get_recording_data(event_main_type, element , element_type, event_type );
try {

 var xhr = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");

     xhr.open('POST', fullthrottlelims_actions_register_url);
     xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

     xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             if( callback_function )
             {
                  //console.log("callback_function");

                  callback_function(event);
             }
         }
     };
     xhr.send(JSON.stringify(submitting_data));

 } catch (error) 
   {
       //console.error('There was a problem with your fetch operation:', error);
    }

}


function get_field_value(element)
{
   //console.log( sha256(element.value) )

   if( is_value_prohibited_to_send( element ) )
   {
       return '';
   }

   let val = element.value;
   if( element.text && ! val )
   {
       val = element.text;
   }

   return val;
}




function is_value_prohibited_to_send(element)
{
    if( element.getAttribute('type') === 'password')
    {
       return true; // no passw
    }

    return false;
}

function sha256(ascii) {
    function rightRotate(value, amount) {
        return (value>>>amount) | (value<<(32 - amount));
    };
    
    var mathPow = Math.pow;
    var maxWord = mathPow(2, 32);
    var lengthProperty = 'length'
    var i, j; // Used as a counter across the whole file
    var result = ''

    var words = [];
    var asciiBitLength = ascii[lengthProperty]*8;
    
    //* caching results is optional - remove/add slash from front of this line to toggle
    // Initial hash value: first 32 bits of the fractional parts of the square roots of the first 8 primes
    // (we actually calculate the first 64, but extra values are just ignored)
    var hash = sha256.h = sha256.h || [];
    // Round constants: first 32 bits of the fractional parts of the cube roots of the first 64 primes
    var k = sha256.k = sha256.k || [];
    var primeCounter = k[lengthProperty];
    /*/
    var hash = [], k = [];
    var primeCounter = 0;
    //*/

    var isComposite = {};
    for (var candidate = 2; primeCounter < 64; candidate++) {
        if (!isComposite[candidate]) {
            for (i = 0; i < 313; i += candidate) {
                isComposite[i] = candidate;
            }
            hash[primeCounter] = (mathPow(candidate, .5)*maxWord)|0;
            k[primeCounter++] = (mathPow(candidate, 1/3)*maxWord)|0;
        }
    }
    
    ascii += '\x80' // Append C' bit (plus zero padding)
    while (ascii[lengthProperty]%64 - 56) ascii += '\x00' // More zero padding
    for (i = 0; i < ascii[lengthProperty]; i++) {
        j = ascii.charCodeAt(i);
        if (j>>8) return; // ASCII check: only accept characters in range 0-255
        words[i>>2] |= j << ((3 - i)%4)*8;
    }
    words[words[lengthProperty]] = ((asciiBitLength/maxWord)|0);
    words[words[lengthProperty]] = (asciiBitLength)
    
    // process each chunk
    for (j = 0; j < words[lengthProperty];) {
        var w = words.slice(j, j += 16); // The message is expanded into 64 words as part of the iteration
        var oldHash = hash;
        // This is now the undefinedworking hash", often labelled as variables a...g
        // (we have to truncate as well, otherwise extra entries at the end accumulate
        hash = hash.slice(0, 8);
        
        for (i = 0; i < 64; i++) {
            var i2 = i + j;
            // Expand the message into 64 words
            // Used below if 
            var w15 = w[i - 15], w2 = w[i - 2];

            // Iterate
            var a = hash[0], e = hash[4];
            var temp1 = hash[7]
                + (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) // S1
                + ((e&hash[5])^((~e)&hash[6])) // ch
                + k[i]
                // Expand the message schedule if needed
                + (w[i] = (i < 16) ? w[i] : (
                        w[i - 16]
                        + (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15>>>3)) // s0
                        + w[i - 7]
                        + (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2>>>10)) // s1
                    )|0
                );
            // This is only used once, so *could* be moved below, but it only saves 4 bytes and makes things unreadble
            var temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) // S0
                + ((a&hash[1])^(a&hash[2])^(hash[1]&hash[2])); // maj
            
            hash = [(temp1 + temp2)|0].concat(hash); // We don't bother trimming off the extra ones, they're harmless as long as we're truncating when we do the slice()
            hash[4] = (hash[4] + temp1)|0;
        }
        
        for (i = 0; i < 8; i++) {
            hash[i] = (hash[i] + oldHash[i])|0;
        }
    }
    
    for (i = 0; i < 8; i++) {
        for (j = 3; j + 1; j--) {
            var b = (hash[i]>>(j*8))&255;
            result += ((b < 16) ? 0 : '') + b.toString(16);
        }
    }
    return result;
};

function can_we_set_onsubmit_handler_for_the_form(form)
{
   let form_id = form.getAttribute('id');
   let form_name = form.getAttribute('name');
   let form_label = form.getAttribute('area-label');

   if( ! form_id && ! form_name && ! form_label )
   {
        return false;
   }

   return true;
}


document.addEventListener( 'DOMContentLoaded' , function()
{
//console.log("Loading");
   do_it();
});
do_it();




})();
(function() {

let detect_ga_details_clientid = null;
let detect_ga_details_sessionid = null;
let detect_ga_details_accountid = null;
let detect_ga_count = 0;
let data_sent = 0;
let fullthrottlelims_client_id = 6490;
let fullthrottlelims_client_type = 1;
let fullthrottlelims_ga_register_url = 'https://hits3.livemarketshoppers.com/'+'gaid.php';

function send_ga_details()
{
   if( data_sent || detect_ga_details_clientid == null || detect_ga_details_sessionid == null || typeof( window.fullthrottle_customerid ) == 'undefined' )
   {
       return;
   }

   data_sent = 1; 

   let submitting_data = {};
       submitting_data.customerid = window.fullthrottle_customerid;
       submitting_data.clientid = fullthrottlelims_client_id;
       submitting_data.client_type = fullthrottlelims_client_type;
       submitting_data.ga_clientid = detect_ga_details_clientid;
       submitting_data.ga_sessionid = detect_ga_details_sessionid;
       submitting_data.ga_accountid = detect_ga_details_accountid;

   try {

    var xhr = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");

        xhr.open('POST', fullthrottlelims_ga_register_url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

        xhr.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
            }
        };
        xhr.send(JSON.stringify(submitting_data));

    } catch (error) 
    {
         console.error('There was a problem with your fetch operation:', error);
    }
}

function detect_ga_details()
{
   if( typeof window.dataLayer == 'undefined' || typeof gtag == 'undefined' ) 
   {
       return false;
   }

   let config_id = null;
   for( i =0; i < window.dataLayer.length; i++ )
   {
       if( window.dataLayer[i][0] == 'config' ) 
       {
           config_id = window.dataLayer[i][1];
           break;
       }
   }

   detect_ga_details_accountid = config_id;
   gtag('get', config_id, 'client_id', (clientId) => {
     detect_ga_details_clientid = clientId;
     send_ga_details();
   });

   gtag('get', config_id, 'session_id', (sessionId) => {
     detect_ga_details_sessionid = sessionId;
     send_ga_details();
   });

   return true;
}

function submit_data()
{
   if( ! data_sent ) 
   {
        send_ga_details();

        setTimeout(submit_data, 100);
   }
}


function do_it()
{
    if( ! detect_ga_details() )
    {
        let pause = 100;
        detect_ga_count++;
        if( detect_ga_count > 10 )
        {
            pause = 1000;
        }

        setTimeout(do_it, pause);
    }

    submit_data();
}


document.addEventListener( 'DOMContentLoaded' , function()
{
    do_it();
});

do_it();

})();