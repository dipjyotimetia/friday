class Friday < Formula
  include Language::Python::Virtualenv
  
  desc "AI Test Case Generator CLI"
  homepage "https://github.com/dipjyotimetia/friday"
  url "https://github.com/dipjyotimetia/friday/archive/refs/tags/v0.1.11.tar.gz"
  sha256 "4296ae90cf7f5455792dac63f89ed67fe9dc06a0269f994b231a13eaca0d26a5"
  license "MIT"

  depends_on "python@3.13"
  depends_on "poetry"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system "poetry", "build"
    venv.pip_install_and_link buildpath
  end

  test do
    assert_match "friday version", shell_output("#{bin}/friday --version")
  end
end