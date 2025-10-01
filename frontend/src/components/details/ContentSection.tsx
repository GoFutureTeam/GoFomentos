import React from 'react';

interface ContentItem {
  title: string;
  content: string;
}

interface ContentSectionProps {
  items: ContentItem[];
}

const ContentSection: React.FC<ContentSectionProps> = ({ items }) => {
  return (
    <div className="space-y-8">
      {items.map((item, index) => (
        <section key={index} className="space-y-4">
          <h2 className="text-[rgba(67,80,88,1)] text-base font-extrabold">
            {item.title}
          </h2>
          <p className="text-black text-[15px] font-medium leading-[30px]">
            {item.content}
          </p>
        </section>
      ))}
    </div>
  );
};

export default ContentSection;