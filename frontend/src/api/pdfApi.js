const API_URL = import.meta.env.VITE_API_URL;

export const parsePdf = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
  
    const res = await fetch(`${API_URL}/api/v1/hashtags/parse_pdf`, {
      method: "POST",
      body: formData,
    });
  
    if (!res.ok) throw new Error("Failed to parse PDF");
  
    return await res.json();
  };
