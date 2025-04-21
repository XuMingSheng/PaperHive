import { useState, useRef } from "react";
import { fetchHashtag } from "../api/hashtagApi";

export const useHashtagInfo = () => {
  const [tagInfo, setTagInfo] = useState({});
  const pending = useRef(new Set());

  const fetchHashtagInfo = async (tag) => {
    if (tagInfo[tag] || pending.current.has(tag)) return;

    pending.current.add(tag);
    try {
      const tag_info = await fetchHashtag(tag)
      setTagInfo((prev) => ({ ...prev, [tag]: tag_info }));
    } catch (err) {
      setTagInfo((prev) => ({ ...prev, [tag]: { name: tag, description: "" } }));
    } finally {
      pending.current.delete(tag);
    }
  };

  return { tagInfo, fetchHashtagInfo };
};
