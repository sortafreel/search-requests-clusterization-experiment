import axios, { AxiosError } from "axios";

const axiosIns = axios.create({
  baseURL: "http://127.0.0.1:8080"
});

export const logErrorToConsole = (error: Error | AxiosError): string => {
  const baseMessage = "Unexpected error. Please, reload the page and try again.";
  let errorMessage;
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.data["detail"]) {
        errorMessage = error.response.data["detail"];
      }
      console.error("ERROR WITH RESPONSE");
      console.error(error.response.data);
      console.error(error.response.status);
      console.error(error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.error("ERROR WITH NO RESPONSE");
      console.error(error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("UNEXPECTED ERROR");
      console.error("Error:", error.message);
    }
  } else {
    console.error("UNEXPECTED ERROR");
    console.error("Error:", error.message);
  }
  return errorMessage || baseMessage;
};

export default axiosIns;
