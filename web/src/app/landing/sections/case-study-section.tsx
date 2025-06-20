// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Bike, Building, Film, Github, Ham, Home, Pizza } from "lucide-react";
import { Bot } from "lucide-react";

import { BentoCard } from "~/components/magicui/bento-grid";

import { SectionHeader } from "../components/section-header";

const caseStudies = [
  {
    id: "eiffel-tower-vs-tallest-building",
    icon: Building,
    title: "埃菲尔铁塔与最高建筑相比有多高？",
    description:
      "该研究比较了埃菲尔铁塔和哈利法塔的高度及其全球意义，并使用 Python 代码计算了倍数关系。",
  },
  {
    id: "github-top-trending-repo",
    icon: Github,
    title: "GitHub 上最热门的仓库有哪些？",
    description:
      "该研究利用 MCP 服务识别出最受欢迎的 GitHub 仓库，并使用搜索引擎对其进行了详细记录。",
  },
  {
    id: "nanjing-traditional-dishes",
    icon: Ham,
    title: "写一篇关于南京传统美食的文章",
    description:
      "该研究通过丰富的内容和图片，生动地展示了南京的著名菜肴，揭示了其背后隐藏的历史和文化意义。",
  },
  {
    id: "rental-apartment-decoration",
    icon: Home,
    title: "如何装饰一间小型出租公寓？",
    description:
      "该研究为读者提供了实用且直接的公寓装饰方法，并配有鼓舞人心的图片。",
  },
  {
    id: "review-of-the-professional",
    icon: Film,
    title: "介绍电影《这个杀手不太冷》",
    description:
      "该研究全面介绍了电影《这个杀手不太冷》，包括其情节、角色和主题。",
  },
  {
    id: "china-food-delivery",
    icon: Bike,
    title: "如何看待中国的外卖大战？（中文）",
    description:
      "该研究分析了京东和美团之间日益激烈的竞争，重点介绍了它们的战略、技术创新和挑战。",
  },
  {
    id: "ultra-processed-foods",
    icon: Pizza,
    title: "超加工食品是否与健康有关？",
    description:
      "该研究探讨了日益增长的超加工食品消费带来的健康风险，并呼吁对长期影响和个体差异进行更多研究。",
  },
  {
    id: "ai-twin-insurance",
    icon: Bot,
    title: '写一篇关于"你会为你的 AI 双胞胎投保吗？"的文章',
    description:
      "该研究探讨了为 AI 双胞胎投保的概念，重点介绍了其好处、风险、伦理考虑以及不断发展的监管。",
  },
];

export function CaseStudySection() {
  return (
    <section className="relative container hidden flex-col items-center justify-center md:flex">
      <SectionHeader
        anchor="case-studies"
        title="案例研究"
        description="通过回放查看 DeerFlow 的实际操作。"
      />
      <div className="grid w-3/4 grid-cols-1 gap-2 sm:w-full sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {caseStudies.map((caseStudy) => (
          <div key={caseStudy.title} className="w-full p-2">
            <BentoCard
              {...{
                Icon: caseStudy.icon,
                name: caseStudy.title,
                description: caseStudy.description,
                href: `/chat?replay=${caseStudy.id}`,
                cta: "点击观看回放",
                className: "w-full h-full",
              }}
            />
          </div>
        ))}
      </div>
    </section>
  );
}
