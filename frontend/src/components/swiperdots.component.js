import React from "react";

function SwiperDots(props) {
  const size = props.style.height;
  switch(props.selected) {
    case 0:
      return (
        <div style={props.style}>
          <div><Dot size={size} selected={true} /></div>
          <div><Dot size={size} selected={false} /></div>
          <div><Dot size={size} selected={false} /></div>
        </div>
      );
    case 2:
      return (
        <div style={props.style}>
          <div><Dot size={size} selected={false} /></div>
          <div><Dot size={size} selected={false} /></div>
          <div><Dot size={size} selected={true} /></div>
        </div>
      );
    default:
      return (
        <div style={props.style}>
          <div><Dot size={size} selected={false} /></div>
          <div><Dot size={size} selected={true} /></div>
          <div><Dot size={size} selected={false} /></div>
        </div>
      );
  }
}
function Dot(props) {
  const opacity = props.selected ? 1 : 0.4;
  return (
    <svg height={props.size} width={props.size}>
      <circle cx={props.size / 2} cy={props.size / 2} r={props.size / 2} strokeWidth="0" fill="white" fillOpacity={opacity}/>
    </svg>
  )
}
export default SwiperDots
