import React from "react";
import HouseIcon from "../assets/svg/houseicon";
import TaxIcon from "../assets/svg/taxicon";

function TypeIcon(props) {
  switch(props.name) {
    case "tax":
      return (<TaxIcon />);
    case "house":
      return (<HouseIcon />);
    default:
      return (<TaxIcon />);
  }
}
export default TypeIcon