import { Component, type ErrorInfo, type ReactNode } from "react";
import { ChartScatter } from "@phosphor-icons/react";

const REPO = "https://github.com/FeiZhuLulu/real-api-pricing";

function isChinese(): boolean {
  try {
    if (localStorage.getItem("pricing-language") === "zh") return true;
  } catch {
    // Language preference is optional.
  }
  return /[#&]lang=zh/.test(location.hash);
}

export default class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Application rendering failed:", error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    const zh = isChinese();

    return (
      <main className="boot" role="alert">
        <ChartScatter size={32} />
        <h1>{zh ? "页面出错了" : "Something went wrong"}</h1>
        <p>
          {zh
            ? "页面渲染出错，重新加载通常即可恢复。"
            : "The page hit an error and stopped rendering. Reloading usually fixes it."}
        </p>
        <div className="boot-actions">
          <button className="primary" onClick={() => location.reload()}>
            {zh ? "重试" : "Try again"}
          </button>
          <a href={REPO}>{zh ? "打开源数据" : "Open the source data"}</a>
        </div>
      </main>
    );
  }
}
