class Friday < Formula
  include Language::Python::Virtualenv
  
  desc "AI Test Case Generator CLI"
  homepage "https://github.com/dipjyotimetia/friday"
  url "https://github.com/dipjyotimetia/friday/archive/refs/tags/v0.1.16.tar.gz"
  sha256 "7f1f0410b86d7270a6833a3bfe0df3c3260ea02d63a7d4514b3276d561c43a0c"
  license "MIT"

  depends_on "python@3.13"
  depends_on "poetry"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system "poetry", "install"
    system "poetry", "build"
    venv.pip_install_and_link buildpath
  end

  test do
    assert_match "friday version", shell_output("#{bin}/friday --version")
  end
end