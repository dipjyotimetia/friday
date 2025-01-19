class Friday < Formula
  include Language::Python::Virtualenv
  
  desc "AI Test Case Generator CLI"
  homepage "https://github.com/dipjyotimetia/friday"
  url "https://github.com/dipjyotimetia/friday/archive/refs/tags/v0.1.21.tar.gz"
  sha256 "e22c87d761e1fd50438c436a58030c677873ca3ea60cc3c9ef618d3b42f259c9"
  license "MIT"

  depends_on "python@3.13"

  def install
    python_exe = Formula["python@3.13"].opt_bin/"python3.13"
    venv = virtualenv_create(libexec, python_exe)
    
    # Ensure pip is available
    venv.pip_install "pip"
    
    # Install dependencies with error handling
    system "#{libexec}/bin/python", "-m", "pip", "install", "-r", "requirements.txt"
    
    # Install the package itself
    system "#{libexec}/bin/python", "-m", "pip", "install", "."

    bin.install Dir[libexec/"bin/*"]
    bin.env_script_all_files(libexec/"bin", 
      PATH: "#{libexec}/bin:$PATH",
      PYTHONPATH: "#{libexec}/lib/python3.13/site-packages:#{ENV["PYTHONPATH"]}"
    )
  end

  test do
    assert_match "friday version", shell_output("#{bin}/friday --version")
  end
end